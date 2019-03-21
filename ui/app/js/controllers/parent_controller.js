/*global: sweetAlert */

/* a middleware the sniffs on AJAX errors */
angular.module("app").factory('errorSniffer', ['$q', function($q) {
  return {
    responseError: function(rejection) {
      if (rejection.status === 401) {
        // Unauthorized
        sweetAlert("Unauthorized", rejection.data, "error");
      } else if (rejection.status === 500) {
        sweetAlert(
          "Internal Server Error",
          "An unexpected server error happened. See the console log for more details.",
          "error"
        );
        console.warn(rejection.status, rejection.data);
      } else if (rejection.status === 502) {
        sweetAlert(
          "Gateway Error (502)",
          "Seems we currently can't connect to the server.",
          "error"
        );
        console.warn(rejection.status, rejection.data);
      } else if (rejection.status === 404) {
        sweetAlert(
          "Page Not Found",
          "A resource was requested that can't be found\n" +
          "(" + rejection.config.method + " " + rejection.config.url + ")",
          "error"
        );
        // console.warn(rejection.status);
      }
      return $q.reject(rejection);
    }
  };
}]);

angular.module("app").config(['$httpProvider', function($httpProvider) {
    $httpProvider.interceptors.push('errorSniffer');
}]);


/* Put things in here that the sub-controllers can use */
angular.module("app").controller('ParentController',
function($scope, $window, $location, $http, Page, Auth0) {
  $scope.Page = Page;
  $scope.isEmpty = isEmpty;
  $scope.fieldIsChanging = fieldIsChanging;
  $scope.humanizeDate = humanizeDate;
  $scope.formatMoment = formatMoment;
  $scope.auth0 = Auth0;
  $scope.loc = $location;
  function updateHttpDefaults() {
    $http.defaults.headers.common["X-Authorization"] = "Bearer " + localStorage.getItem("accessToken");
  }
  $scope.initiateLogin = function() {
    // Do the login in a new window, and set-up token renewal
    // when it completes.
    var loginWindow = $window.open('/auth0_login', '_blank');
    var timer = setInterval(function() {
      if (loginWindow.closed) {
        clearInterval(timer);
        $scope.$apply();
        if (Auth0.isAuthenticated()) {
          Auth0.scheduleRenewal(updateHttpDefaults);
          updateHttpDefaults();
        }
      }
    }, 500);
  };
});
