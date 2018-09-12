$cur = $("#home") ;

$(document).ready(function() {
    // $cur.addClass('active');
    update("home");
});

function update(name){
    var div = document.getElementById("talk");
    div.innerHTML="";
    div.style.display="none";

    $("[name='" + $cur.attr("id") + "']").hide();
    $cur = $("#" + name);
    deactive();
    $cur.addClass('active');
    $cur.show() ;

    var pic = "gate" ;
    if(name == "date"){
      pic = "lake";
    }
    else if(name == "academic"){
      pic = "baijiang";
    }
    else if(name == "patent"){
      pic = "building";
    }
    else if(name == "service"){
      pic = "lake";
    }
    else if(name == "call"){
      pic = "flower";
    }
    else if(name == "reg"){
      pic = "lake2";
    }
    else if(name == "venue"){
      pic = "flower";
    }
    else if(name == "committee"){
      pic = "tower";
    }
    else if(name == "program"){
      pic = "tower";
    }
    // var pic = "gate";
    // if(name == "home"){
    //     pic = "gate" ;
    // } 
    // else if(name == "keynote"){
    //   pic = "keynote" ;
    // }
    // else if(name == "venue" || name == "committee" || name == "program"){
    //     pic = "building" ;
    // }
    // else {
    //     pic = "lake" ;
    // }

    document.getElementById('bg').src = './files/bg/' + 'banner' + '.jpg';
    $("[name='" + $cur.attr("id") + "']").fadeIn("slow") ;
   

	if(name== "academic"){
		loadPaper();
	} else if(name=="home"){
        //loadNews("files/doc/news.csv");
    } else if(name =="service"){
        loadService();
    } else if(name == "patent"){
		loadPatent();
    } else if(name == "download"){
        loadSlide("files/doc/slide.csv");
    }

    // if( name == "venue" ) {
    //     loadmap();
    // }
}

function loadPaper(){
	var file = "files/doc/paper.csv"
	var rawFile = new XMLHttpRequest();
	rawFile.open("GET", file, true);
	rawFile.onreadystatechange = function ()
{
          if(rawFile.readyState === 4)
          {
              if(rawFile.status === 200 || rawFile.status == 0)
              {
				$("#paper-list").html("");
                  var allText = rawFile.responseText;
                  var strings = allText.split('\n');
				for(var line = 0; line < strings.length; line++) {
					var eleList = document.createElement("li");
					if(strings[line]==""){
						continue;
					}
					eleList.innerHTML=strings[line];
					document.getElementById('paper-list').insertBefore(eleList, null);
				}	

              }
          }
      }
      rawFile.send(null);
}

function loadPatent(){
	var file = "files/doc/patent.csv"
	var rawFile = new XMLHttpRequest();
	rawFile.open("GET", file, true);
	rawFile.onreadystatechange = function ()
{
          if(rawFile.readyState === 4)
          {
              if(rawFile.status === 200 || rawFile.status == 0)
              {
				$("#patent-list").html("");
                  var allText = rawFile.responseText;
                  var strings = allText.split('\n');
				for(var line = 0; line < strings.length; line++) {
					var eleList = document.createElement("li");
					if(strings[line]==""){
						continue;
					}
					eleList.innerHTML=strings[line];
					document.getElementById('patent-list').insertBefore(eleList, null);
				}	

              }
          }
      }
      rawFile.send(null);
}


function loadService(){
	var file = "files/doc/service.csv"
	var rawFile = new XMLHttpRequest();
	rawFile.open("GET", file, true);
	rawFile.onreadystatechange = function ()
{
          if(rawFile.readyState === 4)
          {
              if(rawFile.status === 200 || rawFile.status == 0)
              {
				$("#service-list").html("");
                  var allText = rawFile.responseText;
                  var strings = allText.split('\n');
				for(var line = 0; line < strings.length; line++) {
					var eleList = document.createElement("li");
					if(strings[line]==""){
						continue;
					}
					eleList.innerHTML=strings[line];
					document.getElementById('service-list').insertBefore(eleList, null);
				}	

              }
          }
      }
      rawFile.send(null);
}


function loadSlide(file){
    var rawFile = new XMLHttpRequest();
      rawFile.open("GET", file, true);
      rawFile.onreadystatechange = function ()
      {
          if(rawFile.readyState === 4)
          {
              if(rawFile.status === 200 || rawFile.status == 0)
              {
                 $("#slide-download").html("");
                  var allText = rawFile.responseText;
                  var strings = allText.split('\n');
                  var title = document.createElement("tr");
                  var col1 = document.createElement("td");
                  col1.style.fontWeight="bold";
                  col1.innerHTML="报告题目";
                  var col2 = document.createElement("td");
                  col2.innerHTML="报告人";
                  col2.style.fontWeight="bold";
                  var col3 = document.createElement("td");
                  col3.innerHTML="下载链接";
                  col3.style.fontWeight="bold";
                  title.insertBefore(col1, null);
                  title.insertBefore(col2, null);
                  title.insertBefore(col3, null);
                  document.getElementById('slide-download').insertBefore(title, null);
                  for(var j = 0, str; str = strings[j]; j++){
                    var elems = str.split(',');
                    if(elems.length < 3){
                      continue;
                    }
                    var row = document.createElement('tr');
                    for(var k = 0, ele; ele = elems[k]; k++){
                        var column = document.createElement('td');
                        column.innerHTML=ele;
                        row.insertBefore(column, null);
                    }
                    document.getElementById('slide-download').insertBefore(row, null);
                  }
                  var widths = [75, 10, 15];
                  var footer = document.createElement('tr');
                  for(var o = 0; o < widths.length; o++){
                      var empty = document.createElement('td');
                      empty.style.width=widths[o] + "%";
                      empty.innerHTML=" ";
                      footer.insertBefore(empty, null);
                  }
                  document.getElementById('slide-download').insertBefore(footer, null);
              }
          }
      }
      rawFile.send(null);
}

function loadNews(file){
  var rawFile = new XMLHttpRequest();
      rawFile.open("GET", file, true);
      rawFile.onreadystatechange = function ()
      {
          if(rawFile.readyState === 4)
          {
              if(rawFile.status === 200 || rawFile.status == 0)
              {
                 $("#news").html("");
                  var allText = rawFile.responseText;
                  var strings = allText.split('\n');
                  var last = null;
                  for(var j = 0, str; str = strings[j]; j++){
                    var elems = str.split('##');
                    var dat = document.createElement('td');
                    dat.innerHTML=elems[0];
                    dat.setAttribute("class", "time");
                    var info = document.createElement('td');
                    info.innerHTML=elems[1];
                    info.setAttribute("class", "news-info");

                    var row = document.createElement('tr');
                    row.insertBefore(dat, null);
                    row.insertBefore(info, null);

                    document.getElementById('news').insertBefore(row, last);
                    last=row;
                  }
              }
          }
      }
      rawFile.send(null);
}

function loadAttendee(file){
    var rawFile = new XMLHttpRequest();
      rawFile.open("GET", file, true);
      rawFile.onreadystatechange = function ()
      {
          if(rawFile.readyState === 4)
          {
              if(rawFile.status === 200 || rawFile.status == 0)
              {
                 $("#attendee").html("");
                  var allText = rawFile.responseText;
                  var strings = allText.split('\n');
                  for(var j = 0, str; str = strings[j]; j++){
                    var elems = str.split('\t');
                    var row = document.createElement('tr');
                    var header = document.createElement('td');
                    if(j == 0){
                        header.innerHTML= "序号";
                    } else{
                        header.innerHTML=j;
                    }
                    row.insertBefore(header, null);
                    for(var k = 0, ele; ele = elems[k]; k++){
                        var column = document.createElement('td');
                        column.innerHTML=ele;
                        row.insertBefore(column, null);
                    }
                    document.getElementById('attendee').insertBefore(row, null);
                  }
                  var widths = [10, 20, 40, 30];
                  var footer = document.createElement('tr');
                  for(var o = 0; o <= strings[0].split('\t').length; o++){
                      var empty = document.createElement('td');
                      empty.style.width=widths[o] + "%";
                      empty.innerHTML=" ";
                      footer.insertBefore(empty, null);
                  }
                  document.getElementById('attendee').insertBefore(footer, null);
              }
          }
      }
      rawFile.send(null);
}


function deactive(){
    $("#home").removeClass('active') ;
    $("#date").removeClass('active') ;
    $("#academic").removeClass('active') ;
    $("#patent").removeClass('active') ;
    $("#service").removeClass('active') ;
    $("#educate").removeClass('active') ;
    $("#venue").removeClass('active') ;
}

var talkObject = null;
function loadTalkInfo(file){
  var rawFile = new XMLHttpRequest();
  rawFile.open("GET", file, true);
  rawFile.onreadystatechange = function ()
  {
      if(rawFile.readyState === 4)
      {
          if(rawFile.status === 200 || rawFile.status == 0)
          {
              var allText = rawFile.responseText;
              talkObject = JSON.parse(allText);
          }
      }
  }
  rawFile.send(null);
}

var lastPerson = null;
function showTalkDetail(name){
    // var div = document.getElementById("talk");
    // if(lastPerson == name){
    //     div.innerHTML="";
    //     div.style.display="none";
    //     lastPerson = null;
    // } else {
    //     lastPerson = name;
    //     var pic = document.getElementById(name);
    //     var pos = getElementLeft(pic);
    //     var width= document.body.clientWidth;
    //     var mid = width / 3 * 2;
    //     var divWidth = 500;
    //     if(pos > mid){
    //         if(pos < divWidth){
    //             divWidth = pos;
    //             pos = 0;
    //         } else{
    //             pos = pos - 500;
    //         }
    //     } else {
    //         pos = pos + 120;
    //         var delta = width - pos;
    //         if(delta < divWidth){
    //           divWidth = delta;
    //         }
    //     }
    //     div.style.width= divWidth + "px";
    //     div.style.left = pos + 'px';
    //     div.style.top = getElementTop(pic) + 'px';



    //     var title = "待定";
    //     var abstract = "";
    //     var intro = "";

    //     for(var i = 0; i < talkObject.length; i++){
    //         if(talkObject[i].name == name){
    //           title = talkObject[i].info.topic;
    //           abstract = talkObject[i].info.abstract;
    //           intro = talkObject[i].info.intro;
    //           break;
    //         }
    //     }

    //     if(title==""){
    //       return ;
    //     }
    //     var text = "<div class='talkInfo'>" +
    //                "<p><strong>报告题目：</strong>" + title + "<br></p>" +
    //                "<p><strong>报告摘要：</strong></p>" +
    //                "<p>" + abstract + "</p>" +
    //                "<p><strong>报告人简介：</strong></p>" +
    //                "<p>" + intro + "</p>" +
    //                "</div>";

    //     div.innerHTML = text;
    //     div.style.display = "block";
    // }
}

function leavePic(){
    // var div = document.getElementById("talk");
    // div.innerHTML="";
    // div.style.display="none";
}

function getElementLeft(element){
  var actualLeft = element.offsetLeft;
  var current = element.offsetParent;
  while (current !== null){
    actualLeft += current.offsetLeft;
    current = current.offsetParent;
  }
  return actualLeft;
}

function getElementTop(element){
  var actualTop = element.offsetTop;
  var current = element.offsetParent;
  while (current !== null){
    actualTop += current.offsetTop;
    current = current.offsetParent;
  }
  return actualTop;
}

// baidu map
function loadmap() {
    var script = document.createElement("script");
    script.type = "text/javascript";
    // script.src = "http://api.map.baidu.com/api?v=2.0&ak=yIyMbumSqkcuRseHnvK2MASp&callback=init";
    script.src="http://api.map.baidu.com/api?v=2.0&ak=wN0z0jIxpM0uYe3sS0QrQMrzGzOd39oT&callback=init";
    document.body.appendChild(script);
}
function init() {
    venure_address();
    //route1();
}

// map for address
function venure_address() {
    var map = new BMap.Map("allmap");
    var point = new BMap.Point(116.320434,39.996555);   // 创建点坐标
    var marker = new BMap.Marker(point);                // 创建标注
    map.addOverlay(marker);
    map.centerAndZoom(point,15);
    map.enableScrollWheelZoom();                        //启用滚轮放大缩小
    var opts = {
        width : 260,                // 信息窗口宽度
        height: 50,                 // 信息窗口高度
        title : "北京大学英杰交流中心",
        enableMessage:false,
        message:"null"
    }
    var infoWindow = new BMap.InfoWindow("地址：北京市海淀区颐和园路5号", opts);  // 创建信息窗口对象
    marker.addEventListener("click", function(){
        map.openInfoWindow(infoWindow,point);
    });
}

// map for route airport
function route1() {
    var map = new BMap.Map("route1");
    map.centerAndZoom(new BMap.Point(121.622638,38.874104), 11);
    var p1 = new BMap.Point(121.622638,38.874104);
    var p2 = new BMap.Point(121.622638,38.874104);
    var driving = new BMap.DrivingRoute(map, {renderOptions:{map: map, autoViewport: true}});
    driving.search(p1, p2);
}


