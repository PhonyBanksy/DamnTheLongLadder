var app = angular.module('myApp', ['ngRoute', 'ngAnimate']);

app.controller('MyCtrl', function($scope, $location) {
    "use strict";
    $scope.isActive = function(route) {
        return route === $location.path(); 
        
  	};
    
    $scope.go = function ( path ) {   
        $location.path( path );
        
         
    };
	$scope.randomphrases = [
		'creating revenue when they had planned to write it off as losses.',
		'enabling them to concentrate on operating thier business.',
		'increasing cashflow to focus on developing thier company.',
		'removing financial strain on thier bottom line.',
		'making opportunites to increase revenue flow.',
		'strengthening profits and reducing risk.',
		'producing results that exceeded their expectations.'];
    
});



app.config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
	"use strict";
	  $httpProvider.defaults.cache = false;
    if (!$httpProvider.defaults.headers.get) {
      $httpProvider.defaults.headers.get = {};
    }
    // disable IE ajax request caching
    $httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
	
  $routeProvider
  
  .when('/', {
	  title : 'Commercial Debt Management - Recovery professionals based in Glasgow and Edinburgh',
	  //descrip: 'No Recovery, No Fee Available. Best Commission Rates Offered. 30 years experience. Delivering outstanding results and maximising customer cashflow.',
      descrip: 'Start Your Debt Recovery Today. Best Commission Rates Offered. 30 years experience. Delivering outstanding results and maximising customer cashflow.',
    templateUrl : 'home.html',
   controller  : 'homeController'
  })
  
 // .when('/about-us', {
	//   title : 'About Us',
	//  descrip: 'Long desc',
  //  templateUrl : 'about-us.html',
//   controller  : 'oneController'
  //})

	.when('/iresolve-legal', {
	   title : 'iResolve Legal - Commercial Litigation Specialists based in Edinburgh and Glasgow.',
	  descrip: 'iResolveLegal is the chosen Dispute Litigation partner of IHJ Collection. It was set up to provide an innovative way to manage and litigate debt on highly sophisticated case management systems.',
    templateUrl : 'iresolve-legal.html',
    controller  : 'iRController'
  })

  .when('/contact-us', {
	   title : 'Contact Us - we provide dependable debt collection services to private and commercial clients across the UK.',
	  descrip: 'IHJ Collection Ltd, 0131 555 0785, info@ihjcollection.co.uk. 105a North High Street Musselburgh, EH21 6JE.  The Centrum Building, 38 Queen Street, Glasgow, G2 3DX',
    templateUrl : 'contact-us.html',
    controller  : 'threeController'
  		})
	  
	
	.when('/our-services', {
	   title : 'Our Services - A long-established debt recovery and credit management company based in Scotland.',
	  descrip: 'Our specialist teams work tirelessly to succeed in recovering millions for businesses of all shapes and sizes every year. We’ve refined our methods to make the process as simple as possible for you.',
    templateUrl : 'our-services.html',
    controller  : 'twoController'
  		})
  	
  		
		.when('/industry/construction', {
	  			title : 'Construction - Electrical supplies, building & timber merchants.',
	  			descrip: 'IHJ Collections works alongside construction businesses, making opportunites to increase revenue flow.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceConstructionController'
		  	})
		.when('/industry/waste-management', {
	  			title : 'Waste Management - Environmental controllers, landfill, recycling companies and specialist waste services.',
	  			descrip: 'IHJ Collections works alongside waste management businesses, producing results that exceeded their expectations.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceWasteController'
  			})
		.when('/industry/hospitality', {
	  			title : 'Hospitality - Meat, food and drink suppliers.',
	  			descrip: 'IHJ Collections works alongside hospitality businesses, increasing cashflow to focus on developing thier company.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceHospitalityController'
  			})
    	.when('/industry/property-factoring', {
	  			title : 'Property Factoring - Rent arrears and sundry charge collection for housing associations, factoring companies, private landlords.',
	  			descrip: 'IHJ Collections works alongside property factoring businesses, removing financial strain on thier bottom line.',
				templateUrl : 'industry.html',
		   		controller  : 'servicePropertyController'
  			})
		.when('/industry/timeshare-recoveries', {
	  			title : 'Timeshare Recoveries - Management charges, maintenance costs, property repossession.',
	  			descrip: 'IHJ Collections works alongside timeshare recovery businesses, enabling them to concentrate on operating thier business.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceTimeshareController'
  			})
		.when('/industry/automative-hire', {
	  			title : 'Automative and Hire - Repair invoices, storage charges hire charges for garages, insurers and accident management companies. ',
	  			descrip: 'IHJ Collections works alongside automative and hire businesses, creating revenue when they had planned to write it off as losses.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceAutoController'
		  	})
		.when('/industry/invoice-financing', {
	  			title : 'Invoice Financing - Commercial recovery for banks and debt purchasers.',
	  			descrip: 'IHJ Collections works alongside invoice financing businesses, making opportunites to increase revenue flow.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceInvoiceController'
  			})
    	.when('/industry/professional-services', {
	  			title : 'Professional Services - Accountancy & legal.',
	  			descrip: 'IHJ Collections works alongside professional service businesses, producing results that exceeded their expectations.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceProfessionalController'
  			})
		.when('/industry/recruitment-companies', {
	  			title : 'Recruitment Companies - Recovering placement commission payments',
	  			descrip: 'IHJ Collections works alongside recruitment businesses, strengthening profits and reducing risk.',
				templateUrl : 'industry.html',
		   		controller  : 'serviceRecruitmentController'
  			})
	
	.when('/late-payment-legislation', {
	  			title : 'Late Payment Legislation - If the debtor fails to pay on time, you are entitled to late payments.',
	  			descrip: 'The Late Payment of Commercial Debts (Interest) Act 1998 entitles you to claim interest, compensation and reasonable costs when a commercial debtor doesn’t pay.',
				templateUrl : 'late-payment-legislation.html',
		   		controller  : 'lplController'
  			})
	
	.when('/privacy', {
	  			title : 'Internet Privacy & Cookies Policy',
	  			descrip: 'This website is the property of IHJ Collection. We take the privacy of all visitors to this Website very seriously and therefore set out in this privacy and cookies policy our position regarding certain privacy matters and the use of cookies on this Website.',
				templateUrl : 'privacy.html',
		   		controller  : 'privacyController'
  			})
    
.otherwise({redirectTo:'/'});
    
}]);

app.run(['$rootScope', '$location','$window', function($rootScope, $location, $window) {
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
        $rootScope.title = current.$$route.title;
		$rootScope.descrip = current.$$route.descrip;
        $rootScope.currHref = current.originalPath;
        
        
        
       
        //$window.ga('set', 'page', { page: $location.path() });
        //$window.ga('send', 'pageview');
        
        //gtag('config', 'UA-151429789-1', {
        gtag('config', 'G-QJK59LQXXR', {
            'page_title' : $rootScope.title,
            'page_path': $location.path()
        });
        
        //console.log($location.path());
        //console.log( $rootScope.currHref, "orginalPath: ", current.originalPath );
		document.getElementById("toggle").checked = false;
    });
}]);


app.controller('homeController', function($timeout) {
	
	var rect = document.getElementById("sectionNoOb");
	var	elemRect = rect.getBoundingClientRect();
	var spanfired = 0;
	
	window.addEventListener("scroll",function() {
		// console.log(window.scrollY, elemRect.top);
		if (window.scrollY >= elemRect.top && spanfired === 0) {
			spanfired = 1;
			document.getElementById("spanNoOb").classList.add("running");
		}
	});
	
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});

app.controller('oneController', function($timeout) {
	

	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});

app.controller('twoController', function($timeout) {
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});

app.controller('iRController', function($timeout) {
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});

app.controller('lplController', function($timeout) {
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});

app.controller('privacyController', function($timeout) {
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});


app.controller('threeController', function($timeout, $scope, $rootScope) {
	
   $rootScope = $scope.service;
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});
app.controller('serviceController', function($timeout) {
	
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
});

app.controller('serviceAutoController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "automative and hire";
	$rootScope.serviceDesc = "Automative and Hire. ";
	$rootScope.serviceDetail = "Repair invoices, storage charges hire charges for garages, insurers and accident management companies. ";
	$rootScope.servImage = "images/AdobeStock_47301733.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-auto.svg";
	//$scope.provisions = ["service aope", "service bope", "service cope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceRecruitmentController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "recruitment";
	$rootScope.serviceDesc = "Recruitment Companies";
	$rootScope.serviceDetail = "Recovering placement commission payments"
	$rootScope.servImage = "images/AdobeStock_174939952.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-recruit.svg";
	//$scope.provisions = ["service dope", "service eope", "service hope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceWasteController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "waste management";
	$rootScope.serviceDesc = "Waste Management";
	$rootScope.serviceDetail = "Environmental controllers, landfill, recycling companies and specialist waste services.";
	$rootScope.servImage = "images/AdobeStock_108890935.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-wastema.svg";
	//$scope.provisions = ["service iope", "service jope", "service kope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceConstructionController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "construction";
	$rootScope.serviceDesc = "Construction";
	$rootScope.serviceDetail = "Electrical supplies, building & timber merchants.";
	$rootScope.servImage = "images/AdobeStock_86361141.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-constru.svg";
	//$scope.provisions = ["service lope", "service mope", "service nope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceHospitalityController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "hospitality";
	$rootScope.serviceDesc = "Hospitality Industry";
	$rootScope.serviceDetail = "Meat, food and drink suppliers.";
	$rootScope.servImage = "images/AdobeStock_118783800.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-hospitali.svg";
	//$scope.provisions = ["service oope", "service pope", "service qope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('servicePropertyController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "property factoring";
	$rootScope.serviceDesc = "Property Factoring";
	$rootScope.serviceDetail = "Rent arrears and sundry charge collection for housing associations, factoring companies, private landlords.";
	$rootScope.servImage = "images/AdobeStock_95388991.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-propertyfa.svg";
	//$scope.provisions = ["service rope", "service sope", "service tope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceTimeshareController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "timeshare recovery";
	$rootScope.serviceDesc = "Timeshare Recoveries";
	$rootScope.serviceDetail = "Management charges, maintenance costs, property repossession.";
	$rootScope.servImage = "images/AdobeStock_126597260.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-timesh.svg";
	//$scope.provisions = ["service uope", "service vope", "service wnope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceInvoiceController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "invoice financing";
	$rootScope.serviceDesc = "Invoice financing";
	$rootScope.serviceDetail = "Commercial recovery for banks and debt purchasers.";
	$rootScope.servImage = "images/AdobeStock_82952548.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-invoicefa.svg";
	//$scope.provisions = ["service xope", "service yope", "service znope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller('serviceProfessionalController', function($timeout, $rootScope, $scope) {
	
	$rootScope.serviceName = "professional service";
	$rootScope.serviceDesc = "Professional Services";
	$rootScope.serviceDetail = "Accountancy & legal.";
	$rootScope.servImage = "images/AdobeStock_130231971.jpeg";
	$rootScope.randomphrase = $scope.randomphrases[Math.floor(Math.random()* $scope.randomphrases.length)];
	$rootScope.servIcon = "images/icon-profser.svg";
	//$scope.provisions = ["service 1ope", "service 2ope", "service 3nope"];
	document.body.scrollTop = $timeout(function(){document.documentElement.scrollTop = 0;},500);
	
});

app.controller("formCtrl", ['$scope', '$http', function ($scope, $http) {
	var form = Array.prototype.slice.call(document.querySelectorAll("form"),0);
	$scope.url = 'contact_form.php';
	$scope.submitForm = function (isValid) {
		
		if(new RegExp("([a-zA-Z0-9]+://)?([a-zA-Z0-9_]+:[a-zA-Z0-9_]+@)?([a-zA-Z0-9.-]+\\.[A-Za-z]{2,4})(:[0-9]+)?(/.*)?").test($scope.query)) {
			  alert("Fobidden URL Inside Query, Please Remove And Submit If You Have A Legitimate Business Interest");
			form.forEach(function(f){
				setTimeout(function(){f.classList.remove("ng-submitted")},500);
			})
		}
		
		else if (isValid) {
			$http.post($scope.url, {"name": $scope.name , "org": $scope.org , "email": $scope.email , "phone": $scope.phone , "query": $scope.query}).
					success(function(data, status){
						$scope.status = status;
						$scope.data = data;
						console.log($scope.data);
                
				//ga('send', { hitType: 'event', eventCategory: 'Contact' , eventAction: 'Submitted', eventLabel: 'AllForm', eventValue: 100});
                gtag('event', 'Submitted', {'event_category': 'Contact','event_label': 'AllForm','value': 100});
				// $scope.reset();
			});
		} 
		
		else {
			alert('Form is not valid');
		}
		
	};
	
}]);

var fired = 0;
var pointer = document.getElementById('dwnPoi');
window.addEventListener("scroll", goAwayPointer, false);
    
function goAwayPointer() {
	
	if(fired === 0) {
	
		pointer.style.bottom = "-15rem";
		pointer.style.opacity = "0";
		fired = 1;	
		
	}else if (pointer === null)
	{
		fired = 1;	
	}
}