
RESULT_FA_GLYPHICONS_OPEN = {
    'FigureResult': 'fa-bar-chart',
    'TableResult': 'fa-table',
    'ContainerResult': 'fa-folder-open',
}

RESULT_FA_GLYPHICONS_CLOSED = {
    'FigureResult': 'fa-bar-chart',
    'TableResult': 'fa-table',
    'ContainerResult': 'fa-folder',
}

angular.module('app', ['ngSanitize'])
.filter('faGlyphiconOpen', function() {
    return function(input) {
        return RESULT_FA_GLYPHICONS_OPEN[input]
    }
})
.filter('faGlyphiconClosed', function() {
    return function(input) {
        return RESULT_FA_GLYPHICONS_CLOSED[input]
    }
})
.controller('appController', function($scope) {
    $scope.results = {}
    for (elm of ANALYSIS_RESULTS.results) {
    	$scope.results[elm.id] = elm
    }
    rootResult = $scope.results[ANALYSIS_RESULTS.root_result]
    $scope.rootResults = rootResult.children.map(id => $scope.results[id])
    console.log($scope.results)
})
.directive('result', function() {
    return {
        templateUrl: 'result.html',
        restrict: 'E',
        scope: {
            result: '=resultData',
            resultDict: '='
        }
    }
})
