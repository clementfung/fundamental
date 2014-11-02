var app = angular.module('funadamental',["angles", "ngAnimate"]);

app.controller('baseController', ['$scope', function($scope) {
	$scope.INVERVAL = 7;		// in days
	$scope.childName = "Curtis";
	$scope.settings = {};
	$scope.defaultSettings = {};
	$scope.savingsBalance = 123;

	$scope.submitChange = function() {
		// submit settings

		console.log('saved', $scope.settings)
	}

	$scope.discardChanges = function() {
		$scope.settings = cloneObject($scope.defaultSettings);
		console.log($scope.settings)
	}

	$scope.getSettings = function() {
		// get settings and update $scope.settings
		return {
			allowance: 30,
			savingsRate: 10,
			loanRate: 20, 
			hasChanged: false
		}
	}

	$scope.settings = $scope.getSettings();
	$scope.defaultSettings = cloneObject($scope.settings);

	function cloneObject(obj) {
	    var clone = {};
	    for(var i in obj) {
	        if(typeof(obj[i])=="object" && obj[i] != null)
	            clone[i] = cloneObject(obj[i]);
	        else
	            clone[i] = obj[i];
	    }
	    return clone;
	}

	$scope.chart = {
	    labels : ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
	    datasets : [
	        {
	            fillColor : "rgba(151,187,205,0)",
	            strokeColor : "#e67e22",
	            pointColor : "rgba(151,187,205,0)",
	            pointStrokeColor : "#e67e22",
	            data : [4, 3, 5, 4, 6]
	        },
	        {
	            fillColor : "rgba(151,187,205,0)",
	            strokeColor : "#f1c40f",
	            pointColor : "rgba(151,187,205,0)",
	            pointStrokeColor : "#f1c40f",
	            data : [8, 3, 2, 5, 4]
	        }
	    ], 
	};
}]);
