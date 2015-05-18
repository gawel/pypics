// Include gulp
var gulp = require('gulp');
var args   = require('yargs').argv;

// Include Our Plugins
var less = require('gulp-less');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var jshint = require('gulp-jshint');

var appFiles = [
  'pypics/static/components/jquery/dist/jquery.min.js',
  'pypics/static/components/angular/angular.min.js',
  'pypics/static/pypics/*.js'
];

gulp.task('fonts', function() {
    return gulp.src('pypics/static/components/font-awesome/fonts/*')
        .pipe(gulp.dest('pypics/static/sdist/fonts/'));
});

// Compile the Less files
gulp.task('less', function() {
    return gulp.src('pypics/static/pypics/*.less')
        .pipe(less())
        .pipe(gulp.dest('pypics/static/sdist/'));
});

// Concatenate js app files
gulp.task('concat', function () {
  return gulp.src(appFiles)
    .pipe(jshint.reporter('default'))
    .pipe(concat('pypics.js'))
//    .pipe(uglify())
    .pipe(gulp.dest('pypics/static/sdist/'));
});

// Concatenate js app files
gulp.task('dist', ['fonts', 'concat', 'less']);

// Watch Files For Changes
gulp.task('watch', function() {
    gulp.watch('pypics/static/pypics/*.less', ['less']);
    gulp.watch(appFiles, ['concat']);
});

// Default Task
gulp.task('default', ['watch']);
