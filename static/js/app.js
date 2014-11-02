var app = angular.module('funadamental',["angles", "ngAnimate"]);
app.config(['$httpProvider', function ($httpProvider) {
  // Intercept POST requests, convert to standard form encoding
  $httpProvider.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
  $httpProvider.defaults.transformRequest.unshift(function (data, headersGetter) {
    var key, result = [];
    for (key in data) {
      if (data.hasOwnProperty(key)) {
        result.push(encodeURIComponent(key) + "=" + encodeURIComponent(data[key]));
      }
    }
    return result.join("&");
  });
}]);

app.controller('baseController', ['$scope', '$http', function($scope, $http) {
	$scope.INVERVAL = 7;		// in days
	$scope.childName = "Loading...";
	$scope.settings = {};
	$scope.defaultSettings = {};
	$scope.savingsBalance = 'Loading...';
	$scope.chequingBalance = 'Loading...';
	$scope.processing = {
		allowance: false,
		savingsRate: false,
		loanRate: false,
	}
	$scope.savingsChart = {}
	$scope.chequingsChart = {}

	$scope.submitChange = function(value) {
		// submit settings
		$scope.processing[value] = true
		var url;
		switch (value){
			case 'allowance':
				url = '/account/set_allowance'
				break;
			case 'savingsRate':
				url = '/account/savings_interest'
				break;
			case 'loanRate':
				url = '/account/loan_interest'
				break;
		}
		var data = {
				venmo_name: 'cfung',
				rate: $scope.settings[value]}
		console.log('sending ', data)
		$http.post(url, data).
			success(function(data) {
				console.log('output: ', data)
				if (data.success) {
					$scope.defaultSettings[value] = $scope.settings[value]
					alert('Change Successful!')
				}
				$scope.processing[value] = false
			})
	}

	$scope.discardChanges = function() {
		$scope.settings = cloneObject($scope.defaultSettings);
		console.log($scope.settings)
	}

	$scope.getSettings = function() {
		// get settings and update $scope.settings
		$http.get('/account/info/cfung').
			success(function(data) {
				console.log(data)
				$scope.childName = data.user_name;
				$scope.chequingBalance = data.chequing_balance;
				$scope.savingsBalance = data.savings_balance;
				$scope.settings.allowance = data.allowance_amount;
				$scope.settings.savingsRate = data.savings_interest_rate;
				$scope.settings.loanRate = data.loan_interest_rate;

				$scope.defaultSettings = cloneObject($scope.settings);
			})
	}

	$scope.getSettings();

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

	$scope.getChart = function() {
		$http.get('/account/savings/history/cfung').
			success(function(data) {
				console.log(data)
				$scope.savingsChart = {
				    labels : data.row,
				    datasets : [
				        {
				        	scaleOverride: true,
				            fillColor : "rgba(151,187,205,0)",
				            strokeColor : "#e67e22",
				            pointColor : "rgba(151,187,205,0)",
				            pointStrokeColor : "#e67e22",
				            data : data.amount,
				            scaleStartValue: 0
				        }
				    ]
				}
		})
		$http.get('/account/chequings/history/cfung').
			success(function(data) {
				console.log(data)
				$scope.chequingsChart = {
				    labels : data.row,
				    datasets : [
				        {
				        	scaleOverride: true,
				            fillColor : "rgba(151,187,205,0)",
				            strokeColor : "#e67e22",
				            pointColor : "rgba(151,187,205,0)",
				            pointStrokeColor : "#e67e22",
				            data : data.amount,
				            scaleStartValue: 0
				        }
				    ]
				}
		})
	};

	$scope.getChart();
}]);
