function show(){
	alert('Hello,JavaScript!');
 }
function contact(x1,y1,x2,y2){
	return Math.sqrt( (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) ) < 10;
}

function strToTime(str){
	let t=new Date();
	let strs=str.split("-")
	t.setFullYear(Number(strs[0]))
	t.setMonth(Number(strs[1])-1)
	t.setDate(Number(strs[2]))
	t.setHours(Number(strs[3]))
	t.setMinutes(Number(strs[4]))
	t.setSeconds(Number(strs[5]))
	return t
}

function dataLeftCompleting(bits, identifier, value){
    value = Array(bits + 1).join(identifier) + value;
    return value.slice(-bits);
}

function timeToStr(time){
	let year=time.getFullYear();
	let month=time.getMonth()+1;
	let day=time.getDate();
	let hour=time.getHours();
	let minute=time.getMinutes();
	let second=time.getSeconds();

	return dataLeftCompleting(4,"0",year)+"-"+
		dataLeftCompleting(2,"0",month)+"-"+
		dataLeftCompleting(2,"0",day)+"-"+
		dataLeftCompleting(2,"0",hour)+"-"+
		dataLeftCompleting(2,"0",minute)+"-"+
		dataLeftCompleting(2,"0",second);
}

function getTrace(mac,start,end){
	var url_trace = "http://localhost:8010/proxy/device/trace";
	var traces = {
		x:Array(),
		y:Array(),
		location:Array(),
		step:Array()
	};

	$.getJSON(url_trace+'?mac='+mac+'&start='+start+'&end='+end, function(data) {
		//data is the JSON string
			code=data["code"];
			if(code!=200){
				return null
			}
	
			var data_ = data["data"][0]["trace"];
			var len = data_.length;
			for(var i=0; i<len; i++) {
					traces.x[i] = data_[i]["x"];
					traces.y[i] = data_[i]["y"];
					traces.location[i] = data_[i]["location"];
					traces.step[i] = data_[i]["step"];
			}
		})
	return traces
}

function clearResults(){
	let myText=document.getElementById("myText");
	let output=myText.getElementsByTagName("p")[0];
	var canvas = document.getElementById("myCanvas");
	if(canvas.getContext){
		canvas.height=canvas.height;
	}
	output.innerHTML="";
}

function query1(){
	clearResults();

	var ct = document.getElementById("content1");
	var groups=ct.getElementsByClassName("group");
	var macA = groups[0].getElementsByTagName("input")[0].value;
	var macB = groups[1].getElementsByTagName("input")[0].value;
	var start=groups[2].getElementsByTagName("input")[0].value;
	var end=groups[3].getElementsByTagName("input")[0].value;
	var traces_A = {
		x:Array(),
		y:Array(),
		location:Array(),
		step:Array()
	};
	var traces_B = {
		x:Array(),
		y:Array(),
		location:Array(),
		step:Array()
	};
	let results=[]
	let st=strToTime(start)
	let et=strToTime(end)
	
	/*
	if(macA===macB){
		alert("MacA cannot be equal to macB")
		return
	}*/

	$.ajaxSettings.async = false;
	traces_A=getTrace(macA,start,end)
	traces_B=getTrace(macB,start,end)
	$.ajaxSettings.async = true;

	if(traces_A==null||traces_B==null){
		alert("Network error")
		return
	}

	var lenA = traces_A.x.length;
	var lenB = traces_B.x.length;
	var beginTime = 100000;
	var endTime = 0;
	for(var i = 0; i<lenA; i++)
	for(var j = 0; j<lenB; j++){
		if( contact(traces_A.x[i],traces_A.y[i],traces_B.x[j],traces_B.y[j]) && Math.abs(traces_A.step[i]-traces_B.step[j])<60 ) {
			let earlier = Math.min(traces_A.step[i],traces_B.step[j]);
			let later = Math.max(traces_A.step[i],traces_B.step[j]);
			//beginTime = Math.min(beginTime,earlier);
			//endTime = Math.max(endTime,later);
			let temp0=new Date()
			temp0.setTime(st.getTime())
			temp0.setSeconds(temp0.getSeconds()+earlier)
			let temp1=new Date()
			temp1.setTime(st.getTime())
			temp1.setSeconds(temp1.getSeconds()+later)
			results.push([temp0,temp1])
		}
	}

	let myText=document.getElementById("myText");
	let output=myText.getElementsByTagName("p")[0];
	if(results.length!=0) {
		str=""
		for(let v of results){
			//console.log(v[0].toString()+"----"+v[1].toString());
			str+=timeToStr(v[0])+"----"+timeToStr(v[1])+"<br>"
		}
		output.innerHTML=str
	}else {
		output.innerHTML="Safe"
	}
}

function query2() {
	clearResults();

	var ct = document.getElementById("content2");
	var groups=ct.getElementsByClassName("group");
	var macA = groups[0].getElementsByTagName("input")[0].value;
	var url_trace = "http://localhost:8010/proxy/device/trace";
	var url_floor = "http://localhost:8010/proxy/floor/list";
	var traces_A = {
		x:Array(),
		y:Array(),
		location:Array(),
		step:Array()
	};
	var lenA;
	var lenC;
	let end=new Date();
	let start=new Date();
	start.setMinutes(start.getMinutes()-10)
	var MACs = [];

	$.ajaxSettings.async = false;
	traces_A=getTrace(macA,timeToStr(start),timeToStr(end))
	if(traces_A==null){
		alert("Network error")
		return
	}
	lenA=traces_A.x.length
	$.getJSON(url_floor, function(data) {
		var Candidate = data["data"];
		lenC = Candidate.length;
		for(var j=0; j<lenC; j++){
			var tmp = false;
			for(var i=0; i<lenA; i++){
				//&&Math.abs(traces_A.step[i]-Candidate[j]["step"])<60
				if(!tmp && contact(traces_A.x[i],traces_A.y[i],Candidate[j]["x"],Candidate[j]["y"])){
					MACs.push(Candidate[j]["mac"]);
					tmp = true;
				}
			}
		}
	})
	$.ajaxSettings.async = true;

	var NoDuplicate = [];  //去重
	var MLen= MACs.length;
	for(var i=0; i<MLen; i++) {
		if(NoDuplicate.indexOf(MACs[i]) === -1) {
			NoDuplicate.push(MACs[i]);
		}
	}
	
	let myText=document.getElementById("myText");
	let output=myText.getElementsByTagName("p")[0];
	if(NoDuplicate.length!=0) {
		str=""
		for(let v of NoDuplicate){
			//console.log(v[0].toString()+"----"+v[1].toString());
			str+=v+"<br>"
		}
		output.innerHTML=str
	}else {
		output.innerHTML="Safe"
	}
}

function query3(){
	clearResults();

	var ct = document.getElementById("content3");
	var groups=ct.getElementsByClassName("group");
	var limit=groups[0].getElementsByTagName("input")[0].value;
	var level=groups[1].getElementsByTagName("input")[0].value;
	var rssi=groups[2].getElementsByTagName("input")[0].value;
	var start=groups[3].getElementsByTagName("input")[0].value;
	var end=groups[4].getElementsByTagName("input")[0].value;
	var url_show = "http://localhost:8010/proxy/floor/show";
	let st=strToTime(start)
	let et=strToTime(end)
	
	var devices = {
		mac:Array(),
		x:Array(),
		y:Array(),
		step:Array()
	};
	$.ajaxSettings.async = false;
	var url = url_show+'?level='+level+'&rssi='+rssi+'&limit='+limit+'&start='+start+'&end='+end;
	//alert(url);
	$.getJSON(url, function(data) {
	//data is the JSON string
		code=data["code"];
		if(code!=200){
			alert("code wrong");
			return null
		}
		var data_ = data["data"];
		var len = data_.length;
		for(var i=0; i<len; i++) {
				devices.x[i] = data_[i]["x"];
				devices.y[i] = data_[i]["y"];
				devices.mac[i] = data_[i]["mac"];
				devices.step[i] = data_[i]["step"];
		}
	})
	$.ajaxSettings.async = true;
	
	var canvas = document.getElementById("myCanvas");
	//检测浏览器是否支持canvas 该方法是否存在 取得上下文对象
    if (canvas.getContext) {
		var context = canvas.getContext("2d");
		canvas.height = canvas.height; 
		var x_begin = 0
		var y_begin = 80
		var canvas_x_len = 550
		var canvas_y_len = 300
		context.fillStyle = "gray";
		context.rect(x_begin,y_begin,canvas_x_len,canvas_y_len);
		context.stroke();
		context.font="10px Arial";
		context.strokeStyle = "black";
		for(var i=0; i<=4; i++) {
			context.beginPath();
			context.moveTo(0,y_begin+canvas_y_len/5*i);
			context.lineTo(5,y_begin+canvas_y_len/5*i);
			context.stroke();
			context.fillText(""+(40-i*10),5,y_begin+canvas_y_len/5*i+2);
		}
		for(var i=1; i<=6; i++) {
			context.beginPath();
			context.moveTo(x_begin+canvas_x_len/6*i,y_begin+canvas_y_len);
			context.lineTo(x_begin+canvas_x_len/6*i,y_begin+canvas_y_len-5);
			context.stroke();
			context.fillText(""+(-10+10*i),x_begin+canvas_x_len/6*i-3,y_begin+canvas_y_len+8)
		}
		
		context.strokeStyle = "blue";
		var x_zero = x_begin+canvas_x_len/6;
		var y_zero = y_begin+canvas_y_len*4/5;
		var x_unit = canvas_x_len/60;
		var x_len = x_unit*42.5;
		var y_unit = canvas_y_len/50;
		var y_len = y_unit*29
		context.rect(x_zero,y_begin+canvas_y_len/5,x_len,y_len);
		context.stroke();

		var inner_x_len=x_unit*23;
		var inner_y_len=y_unit*8;
		var inner_x_zero=x_begin+x_unit*20;
		var inner_y_zero=y_begin+y_unit*20;
		context.rect(inner_x_zero,inner_y_zero,inner_x_len,inner_y_len);
		context.stroke();

		/*
		for(var i=0; i<20;i++) {
			devices.x[i] = Math.random()*42.5;
			devices.y[i] = Math.random()*29;
		}  //测试画图功能
		*/
		var num_devices = devices.x.length;
		var colors = new Array("red","yellow","blue","green");
		for (var i=0; i<num_devices; i++) {
			var x = devices.x[i];
			var y = devices.y[i];
			context.fillStyle = colors[i%4];
			context.beginPath();
			context.arc(x_zero+x*x_unit,y_zero-y*y_unit,2,0,2*Math.PI);
			context.fill();
		}
	}
}

function query4() {
	clearResults();

	var ct = document.getElementById("content4");
	var groups=ct.getElementsByClassName("group");
	//var level = groups[0].getElementsByTagName("input")[0].value;
	var url_floor = "http://localhost:8010/proxy/floor/list";
	var MACs = [];

	$.ajaxSettings.async = false;
	$.getJSON(url_floor, function(data) {
		var Candidate = data["data"];
		lenC = Candidate.length;
		for(var j=0; j<lenC; j++){
			MACs.push([Candidate[j]["mac"],Candidate[j]["x"],Candidate[j]["y"]]);
		}
	})
	$.ajaxSettings.async = true;

	/*
	var NoDuplicate = [];  //去重
	var MLen= MACs.length;
	for(var i=0; i<MLen; i++) {
		if(NoDuplicate.indexOf(MACs[i]) === -1) {
			NoDuplicate.push(MACs[i]);
		}
	}
	*/
	
	let myText=document.getElementById("myText");
	let output=myText.getElementsByTagName("p")[0];
	if(MACs.length!=0) {
		str=""
		for(let v of MACs){
			//console.log(v[0].toString()+"----"+v[1].toString());
			str+=v[0]+": ("+v[1]+","+v[2]+")"+"<br>";
		}
		output.innerHTML=str
	}else {
		output.innerHTML="No active devices!"
	}
}

function query5(){
	clearResults();

	var ct = document.getElementById("content5");
	var groups=ct.getElementsByClassName("group");
	var macA = groups[0].getElementsByTagName("input")[0].value;
	var start=groups[1].getElementsByTagName("input")[0].value;
	var end=groups[2].getElementsByTagName("input")[0].value;
	var traces_A = {
		x:Array(),
		y:Array(),
		location:Array(),
		step:Array()
	};
	let st=strToTime(start)
	let et=strToTime(end)
	
	$.ajaxSettings.async = false;
	traces_A=getTrace(macA,start,end)
	$.ajaxSettings.async = true;

	if(traces_A==null){
		alert("Network error")
		return
	}

	let myText=document.getElementById("myText");
	let output=myText.getElementsByTagName("p")[0];
	len=traces_A.x.length;
	
	if(len!=0) {
		str=""
		for(let i=0;i<len;i++){
			str+="("+traces_A.x[i]+","+traces_A.y[i]+")"+"<br>"
		}
		output.innerHTML=str

		var canvas = document.getElementById("myCanvas");
		//检测浏览器是否支持canvas 该方法是否存在 取得上下文对象
		if (canvas.getContext) {
			var context = canvas.getContext("2d");
			canvas.height = canvas.height; 
			var x_begin = 0
			var y_begin = 80
			var canvas_x_len = 550
			var canvas_y_len = 300
			context.fillStyle = "gray";
			context.rect(x_begin,y_begin,canvas_x_len,canvas_y_len);
			context.stroke();
			context.font="10px Arial";
			context.strokeStyle = "black";
			for(var i=0; i<=4; i++) {
				context.beginPath();
				context.moveTo(0,y_begin+canvas_y_len/5*i);
				context.lineTo(5,y_begin+canvas_y_len/5*i);
				context.stroke();
				context.fillText(""+(40-i*10),5,y_begin+canvas_y_len/5*i+2);
			}
			for(var i=1; i<=6; i++) {
				context.beginPath();
				context.moveTo(x_begin+canvas_x_len/6*i,y_begin+canvas_y_len);
				context.lineTo(x_begin+canvas_x_len/6*i,y_begin+canvas_y_len-5);
				context.stroke();
				context.fillText(""+(-10+10*i),x_begin+canvas_x_len/6*i-3,y_begin+canvas_y_len+8)
			}
			
			context.strokeStyle = "blue";
			var x_zero = x_begin+canvas_x_len/6;
			var y_zero = y_begin+canvas_y_len*4/5;
			var x_unit = canvas_x_len/60;
			var x_len = x_unit*42.5;
			var y_unit = canvas_y_len/50;
			var y_len = y_unit*29
			context.rect(x_zero,y_begin+canvas_y_len/5,x_len,y_len);
			context.stroke();

			var inner_x_len=x_unit*23;
			var inner_y_len=y_unit*8;
			var inner_x_zero=x_begin+x_unit*20;
			var inner_y_zero=y_begin+y_unit*20;
			context.rect(inner_x_zero,inner_y_zero,inner_x_len,inner_y_len);
			context.stroke();

			/*
			for(var i=0; i<20;i++) {
				devices.x[i] = Math.random()*42.5;
				devices.y[i] = Math.random()*29;
			}  //测试画图功能
			*/

			context.strokeStyle = "green";
			for (var i=0; i<len-1; i++) {
				var startx = traces_A.x[i]
				var endx = traces_A.x[i+1]
				var starty = traces_A.y[i]
				var endy = traces_A.y[i+1]
				context.beginPath();
				context.moveTo(x_zero+startx*x_unit,y_zero-starty*y_unit)
				context.lineTo(x_zero+endx*x_unit,y_zero-endy*y_unit)
				context.stroke();
			}
		}
	}else {
		output.innerHTML="No query results!"
	}
}