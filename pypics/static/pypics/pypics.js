/*jslint browser: true, indent: 4, sloppy: true */
/*global $, angular */

var pypics = angular.module('pypics', []);

pypics.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});


function PhotoCtrl($scope, $window) {
    $scope.size = {"height": $window.innerHeight + "px"};
    $scope.image_size = {"height": ($window.innerHeight-20) + "px"};
    $($window).resize(function () {
        $scope.size = {"height": $window.innerHeight + "px"};
        $scope.image_size = {"height": ($window.innerHeight-20) + "px"};
        $scope.$apply();
    });
}

function Photo(attrs) {
    $.extend(this, attrs);
}

function SetCtrl($scope, $window) {
    $scope.photos = [];
    $scope.current = 0;

    $scope.anchor = function() {
        return $window.location.hash;
    };

    $scope.show = function(i) {
        $window.location.hash = '#' + i;
        $scope.current = i;
    };

    $scope.hide = function() {
        $window.location.hash = '';
        $scope.current = 0;
    };

    $scope.resize = function (apply) {
        $scope.size = {"height": $window.innerHeight + "px"};
        $scope.image_size = {"height": ($window.innerHeight-20) + "px"};
        if (apply) { $scope.$apply(); }
    };
    $($window).resize(function () { $scope.resize(true); });
    $scope.resize(false);

    $scope.next = function() {
        if ($scope.current < $scope.photos.length - 1) {
            $scope.current += 1;
            $window.location.hash = '#' + $scope.current;
        } else {
            $scope.hide();
        }
    };

    $scope.previous = function() {
        if ($scope.current >= 1) {
            $scope.current -= 1;
            $window.location.hash = '#' + $scope.current;
        } else {
            $scope.hide();
        }
    };

    $scope.init = function() {
        $('.set a').each(function () {
            var a = $(this),
                i = $('img', a);
            $scope.photos.push(new Photo({
                "title": a.attr('title'),
                "index": a.attr('id'),
                "href": a.attr('href'),
                "src": a.attr('rel'),
                "thumbnail": i.attr('src')
            }));
            a.removeAttr('href');
        });
        if ($window.location.hash) {
            $scope.current = parseInt($window.location.hash.replace('#', ''), 0);
        }
    };
}
