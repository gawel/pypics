/*jslint browser: true, indent: 4, sloppy: true */
/*global $, angular */

var pypics = angular.module('pypics', []);

pypics.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});


function PhotoCtrl($scope) {
    $scope.size = {"height": window.innerHeight + "px"};
    $(window).resize(function () {
        $scope.size = {"height": window.innerHeight + "px"};
        $scope.$apply();
    });
}

function Photo(attrs) {
    $.extend(this, attrs);
}

function SetCtrl($scope) {
    $scope.photos = [];
    $scope.current = 0;

    $scope.resize = function (apply) {
        $scope.size = {"height": window.innerHeight + "px"};
        $scope.image_size = {"height": (window.innerHeight-20) + "px"};
        if (apply) { $scope.$apply(); }
    };
    $(window).resize(function () { $scope.resize(true); });
    $scope.resize(false);

    $scope.next = function() {
        if ($scope.current < $scope.photos.length - 1) {
            $scope.current += 1;
        }
    };

    $scope.previous = function() {
        if ($scope.current > 1) {
            $scope.current -= 1;
        }
    };

    $scope.init = function() {
        $('.set a').each(function () {
            var a = $(this),
                i = $('img', a);
            $scope.photos.push(new Photo({
                "title": a.attr('title'),
                "href": a.attr('href'),
                "src": a.attr('rel'),
                "thumbnail": i.attr('src')
            }));
        });
    };
}
