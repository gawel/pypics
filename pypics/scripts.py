# -*- coding: utf-8 -*-
import jinja2
from operator import attrgetter
from collections import defaultdict
from ConfigObject import ConfigObject
from datetime import datetime
from chut import cp, test, path, env, find, pwd, mkdir
from chut import info, debug
import chut as sh
import os

env.lc_all = 'C'

aptitude = []

if sh.which('exif'):
    EXIF_AVAILABLE = True
else:
    EXIF_AVAILABLE = False
    print('exif binary is not available')
    aptitude.append('exif')

if sh.which('convert'):
    CONVERT_AVAILABLE = True
else:
    CONVERT_AVAILABLE = False
    print('convert binary is not available')
    aptitude.append('imagemagick')

if sh.which('convert'):
    JHEAD_AVAILABLE = True
else:
    JHEAD_AVAILABLE = False
    print('jhead binary is not available')
    aptitude.append('jhead')

if aptitude:
    print('Please run:')
    print('$ sudo aptitude install %s' % ' '.join(aptitude))


def safe_unicode(value):
    if isinstance(value, str):
        return value.decode('utf8')
    return value


class Photo(ConfigObject):

    __name__ = 'photo'

    def __init__(self, filename):
        filename = filename.strip()
        if not filename.endswith('.metadata'):
            filename += '.metadata'
        super(Photo, self).__init__(filename=filename)
        if not self.exif.items() and EXIF_AVAILABLE:
            self.parse_exif()
            self.write()

    def __getattr__(self, attr):
        if attr in ('title', 'description'):
            return safe_unicode(self.metadata[attr])
        if attr.startswith('thumb_'):
            return self.thumbnail(size=attr.split('_'))
        return super(Photo, self).__getattr__(attr)

    def rotate(self, original=None):
        filename = self.filename[:-9]
        if not original:
            original = filename
        if path.abspath(original) != path.abspath(filename):
            info('Copying %s...' % filename)
            debug(cp(original, filename))
        if JHEAD_AVAILABLE:
            debug('Rotating %s...' % filename)
            debug(sh.jhead('-autorot -norot', filename))
            self.parse_exif()
            self.write()

    @property
    def title(self):
        title = self.metadata.title
        if not title:
            filename = self.filename[len(pwd()) + 1:-9]
            return path.basename(filename)
        return safe_unicode(title)

    @property
    def path(self):
        filename = self.filename[len(pwd()) + 1:-9]
        filename, _ = path.splitext(filename)
        return '/' + filename + '/'

    @property
    def url(self):
        return self.path

    def thumbnail(self, size=200):
        filename = self.filename[len(pwd()) + 1:-9]
        url = '/thumbs/%(s)sx%(s)s/' % dict(s=size)
        return url + filename

    def photo(self):
        url = self.thumbnail(size=1280)
        return url

    @property
    def output_filename(self):
        return path(self.path.lstrip('/'), 'index.html')

    @property
    def tags(self):
        return self.metadata.tags.as_list()

    @property
    def date(self):
        date = self.metadata.date
        for f in ('%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(date, f)
            except ValueError:
                continue
        return datetime(1900, 1, 1)

    def parse_exif(self):
        filename = self.filename[:-9]
        if EXIF_AVAILABLE:
            debug('Processing exif for %s' % filename)
            data = {}
            sh.env.lc_all = "C"
            for line in sh.exif('--xml-output', filename):
                if '</' in line:
                    line = line.strip()
                    key, value = line.split('>', 1)
                    value = value.split('</', 1)[0]
                    if not value or 'unknow' in value.lower():
                        continue
                    key = key.strip('< ')
                    if '__' in key:
                        continue
                    data[key] = value
            self.exif = data
            if 'Date_and_Time' in data:
                date = data['Date_and_Time']
                self.metadata.date = date
                tags = self.tags
                if date[:4] not in tags:
                    tags.insert(0, date[:4])
                self.metadata.tags = tags
        if not self.metadata.date:
            now = datetime.now()
            self.metadata.date = now.strftime('%Y-%m-%d %H:%M:00')
            self.exif.Date_and_Time = self.metadata.date

    def __repr__(self):
        return '<Photo for %r>' % self.filename[len(pwd()) + 1:-9]


def auto_update():
    sh.wget(
        '-qO .git/hooks/post-update --no-check-certificate',
        'https://raw.github.com/gawel/pypics/master/scripts/post-update'
    ) > 1


class Container(list):

    @property
    def title(self):
        return self.name

    @property
    def path(self):
        return '/' + self.name + '/'

    @property
    def url(self):
        return self.path

    @property
    def output_filename(self):
        return path(self.path.lstrip('/'), 'index.html')

    @property
    def object_list(self):
        return list(sorted(self, key=attrgetter('date')))

    def __getattr__(self, attr):
        return getattr(self.object_list[0], attr)

    def __repr__(self):
        return '<%s %r (%s items)>' % (self.__class__.__name__,
                                       self.name, len(self))


class Set(Container):

    __name__ = 'set'

    @property
    def name(self):
        return path.dirname(self[0].filename)[len(pwd()) + 1:]


class Tag(Container):

    __name__ = 'tag'
    __alt__ = 'set'

    def __init__(self, name):
        self.name = name

    @property
    def path(self):
        return path('/tags', self.name) + '/'


class Index(object):

    __name__ = 'index'

    PhotoClass = Photo

    def __init__(self, **config):
        self.sizes = (200, 600, 1280)
        self.build_path = config.get('build_path', 'build')
        package = os.path.dirname(__file__)
        self.static_dir = path(package, 'static', 'sdist')

        metadatas = [self.PhotoClass(p)
                     for p in find(pwd(), '-name *metadata')]
        self.metadatas = metadatas

        templates = config.get('templates_path', [])
        templates = [path.abspath(p) for p in templates]
        templates.append(path(package, 'templates'))
        self.templates = templates
        loader = jinja2.FileSystemLoader(self.templates)
        self.env = jinja2.Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_resources(self):
        javascripts = sorted(find(
            self.static_dir, r'-name *.js'), reverse=True)
        stylesheets = list(find(
            self.static_dir, r'-name *.css'))

        l = len(self.static_dir) + 1
        resources = dict(
            stylesheets=['/static/sdist/' + r[l:] for r in stylesheets],
            javascripts=['/static/sdist/' + r[l:] for r in javascripts],
        )
        sh.rsync('-r', self.static_dir,
                 path(self.build_path, 'static/')) > 1
        return resources

    def resize(self):
        processes = []
        for filename in find(pwd(), '-name *metadata'):
            filename = filename.strip()[len(pwd()) + 1:-9]
            for size in self.sizes:
                xsize = '%sx%s' % (size, size)
                thumb = path(self.build_path, 'thumbs', xsize, filename)
                if test.f(thumb):
                    continue
                sh.mkdir('-p', path.dirname(thumb)) > 1
                if size > 600:
                    msize = '%sx%s' % (size + 200, size + 200)
                    processes.append(' '.join([
                        '-define jpeg:size=' + msize,
                        filename, '-antialias -thumbnail', xsize,
                        thumb]))
                else:
                    processes.append(' '.join([
                        '-define jpeg:size=' + xsize,
                        filename, '-thumbnail', xsize + '^',
                        '-gravity center -extent', xsize, thumb]))
        for p in sh.convert.map(processes, stop_on_failure=True, pool_size=3):
            pass

    def generate(self):
        sets = defaultdict(Set)
        tags = dict()
        for meta in reversed(self.metadatas):
            sets[path.dirname(meta.filename)].append(meta)
            for name in meta.tags:
                tag = tags.setdefault(name, Tag(name))
                tag.append(meta)

        context = dict(
            all_sets=sorted(sets.values(), key=lambda o: o.name, reverse=True),
            all_tags=sorted(tags.values(), key=lambda o: o.name),
            sorted=sorted,
            enumerate=enumerate,
            path=path,
            env=env,
            u=safe_unicode,
        )
        context.update(self.get_resources())

        debug(context['all_sets'])

        self.render(self, **context)
        for container in sets.values() + tags.values():
            debug(container)
            self.render(container,
                        title=container.name,
                        container=container,
                        **context)
            if isinstance(container, Set):
                for index, photo in enumerate(container.object_list):
                    self.render(photo,
                                index=index,
                                container=container,
                                **context)

    @property
    def path(self):
        return '/'

    @property
    def url(self):
        return self.path

    @property
    def output_filename(self):
        return 'index.html'

    def render(self, item, **kwargs):
        name = item.__name__.lower()
        template = name + '.html'
        filename = path(self.build_path, item.output_filename)
        try:
            self.render_template(template, filename=filename,
                                 object=item, **kwargs)
        except jinja2.exceptions.TemplateNotFound:
            name = getattr(item, '__alt__', '')
            if name:
                template = name + '.html'
                filename = path(self.build_path, item.output_filename)
                self.render_template(template, filename=filename,
                                     object=item, **kwargs)
            else:
                raise

    def render_template(self, tmpl, **kwargs):
        template = self.env.get_template(tmpl)
        filename = kwargs.get('filename', path(self.build_path, tmpl))
        mkdir('-p', path.dirname(filename))
        data = template.render(**kwargs).encode('utf8')
        with open(filename) as fd:
            if fd.read() != data:
                with open(filename, 'w') as fd:
                    fd.write(data)


@sh.console_script(fmt='brief')
def pics(args):
    """
    Usage: %prog (update|serve) [options]
           %prog add [options] <image>...
           %prog set [options] <key> <value>
           %prog (addtag|deltag) [options] <tag>...

    Options:

    -u URL, --url=URL   Absolute url to use
    -t, --thumbs        Generate thumbs
    -d, --directory     A directory containing images [default: .]
    %options
    """
    build_path = os.path.abspath('build')
    pics = Index(build_path=build_path)
    if args['--thumbs']:
        pics.resize()
    url = args['--url'] or ''
    env.url = url.strip('/')
    if args['serve']:
        os.chdir(pics.build_path)
        from serve import serve
        serve()
    elif args['update']:
        pics.generate()
    elif args['deltag']:
        for filename in find('-name *.metadata'):
            filename = filename.strip()
            config = ConfigObject(filename=filename)
            tags = config.metadata.tags.as_list()
            tags = [t for t in tags if t not in args['<tag>']]
            config.metadata.tags = tags
            config.write()
    elif args['addtag']:
        for filename in find('-name *.metadata'):
            filename = filename.strip()
            config = Photo(filename=filename)
            tags = config.metadata.tags.as_list()
            tags.extend([t for t in args['<tag>'] if t not in tags])
            config.metadata.tags = tags
            config.write()
    elif args['set']:
        for filename in find('-name *.metadata'):
            filename = filename.strip()
            config = ConfigObject(filename=filename)
            if not config.metadata.date:
                now = datetime.now()
                config.metadata.date = now.strftime('%Y-%m-%d')
            section = 'metadata'
            key = args['<key>']
            if key.lower() in ('exif.date_and_time', 'exif.date'):
                key = 'exif.Date_and_Time'
            if '.' in key:
                section, key = key.split('.')
            value = args['<value>']
            config[section][key] = value
            if key == 'Date_and_Time':
                config.metadata.date = value

            config.write()
    elif args['add']:
        for filename in args['<image>']:
            filename = path.expanduser(filename.strip())
            if path.splitext(filename)[1].lower() not in ('.jpg',):
                continue
            if path.isfile(filename + '.metadata'):
                continue
            new_filename = path.basename(filename).replace(' ', '_')
            config = Photo(filename=new_filename)
            config.rotate(original=filename)
            config.write()
