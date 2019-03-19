var http = require('http');
var axios = require('axios');
var qs = require('querystring');
axios.defaults.baseURL = 'http://api.evidentli.com';
var port = 8082;


console.log('listening on port '+ port);
http.createServer(function(proxyRequest, proxyResponse) {
	var body = '';
	var json_body = {}; 

	proxyRequest.on('data', function(data){
		console.log('incoming data')
		body += data;
	});

	proxyRequest.on('end', function(){
		console.log('ending request');
		if(body){
			json_body = JSON.parse(body);
		}

		var responseHeaders = { 'Access-Control-Allow-Origin':'*',
		'Access-Control-Allow-Headers':'Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers',
		'Access-Control-Allow-Methods': 'GET,HEAD,OPTIONS,POST,PUT',
		'Access-Control-Allow-Credentials': "true",
		'Content-Type': 'application/json',
		'X-Application-Context': 'application',
		'Connection': 'close'
		};
		//console.log(responseHeaders);
		if(proxyRequest.method == 'OPTIONS'){ //preflight CORS request
			proxyResponse.writeHead(200, responseHeaders);
			proxyResponse.end('POST, GET, PUT');
		} else if(['GET', 'POST', 'PUT'].includes(proxyRequest.method)){
			axios.request({method: proxyRequest.method, url: proxyRequest.url, data: json_body}).then(serverResponse => { 
				if(typeof(serverResponse.data)==='object'){
					var content = JSON.stringify(serverResponse.data);
					var contentLength = Buffer.byteLength(content,'utf8');
					responseHeaders['content-length'] = contentLength;
					console.log(responseHeaders);
					proxyResponse.writeHead(200, responseHeaders);
					proxyResponse.end(content);
				} else {
					errorResponse(proxyResponse, 'Invalid json');
				}
			}).catch(e => errorResponse(proxyResponse, e));
		}
	});

}).listen(port);

function errorResponse(response, e){
	response.writeHead(400, {'Content-Type': 'text/plain'});
	response.end('400 Bad Request: ' + e);
}
