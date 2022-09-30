function initSeaDragon(imgpath, docobj) {
  if(!docobj){
    docobj = document;
  }
  var Viewer = OpenSeadragon({
      id: "openseadragon1",
      prefixUrl: "/static/openseadragon_images/",
      tileSources: {
	  type: 'image',
	  url: imgpath
      },
      buildPyramid: false
  });
  Viewer.addHandler('open', function(){
    // true makes it happen immediately
    var coords = {'x': parseFloat(docobj.getElementById("orig_state_x").value),
		  'y': parseFloat(docobj.getElementById("orig_state_y").value)}
    var center = new OpenSeadragon.Point(coords.x, coords.y);
    var zoomLevel = parseFloat(docobj.getElementById("orig_state_zoom").value)
    if(zoomLevel || zoomLevel == 0){
      console.log("activity");
      c2 = coords;
      console.log(coords);
      Viewer.viewport.zoomTo(zoomLevel, null, true);
      Viewer.viewport.panTo(center, true);
    }
  });
  function stateChangeHandler() {
    var coords = Viewer.viewport.getCenter();
    var zoomLevel = Viewer.viewport.getZoom();
    var currentState = {"x": coords.x, "y": coords.y, "zoom": zoomLevel};
    for(var i=0; i< docobj.forms.length; i++) {
      var x = docobj.forms[i]; 
      dude = x;
      var coordStateX = x.querySelector("input[name='state_x']");
      var coordStateY = x.querySelector("input[name='state_y']");
      var coordStateZoom = x.querySelector("input[name='state_zoom']");
      var formState = {"x": coordStateX, "y":coordStateY, "zoom":coordStateZoom};
      for (var state in formState) {
	stateVal = formState[state];
	if(stateVal){
	  stateVal.value = currentState[state];
	}
	else {
	  var toAppend = createElementFromHTML("<input type='hidden' name='state_" + state +"' value='"+currentState[state] + "' />");
	  x.appendChild(toAppend);
	}
      }
    }
    if (docobj.querySelector("#latest_state_x")) {
      docobj.querySelector("#latest_state_x").value = currentState["x"];
      docobj.querySelector("#latest_state_y").value = currentState["y"];
      docobj.querySelector("#latest_state_zoom").value = currentState["zoom"];
    }
    return true;
  }
  Viewer.addHandler('zoom', stateChangeHandler);
  Viewer.addHandler('pan', stateChangeHandler);
}

function createElementFromHTML(htmlString) {
  var div = document.createElement('div');
  div.innerHTML = htmlString.trim();

  // Change this to div.childNodes to support multiple top-level nodes.
  return div.firstChild;
}

function get_url_path(pathstr){
  return encodeURIComponent(pathstr);
}

let params = "scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=600,height=300,left=100,top=100";
var newWin = null;
function popOut(endpoint, imgpath, alreadyOpen){
   full_url = endpoint + "?imgpath=" + get_url_path(imgpath);
   if(alreadyOpen){
     newWin = open("", "image");
   }
   else {
     newWin = open(full_url, "image", params);
   }

   if(newWin.location.pathname == "/static/waiting.html"){
     console.log("AHA");
     newWin.location.href = full_url;
     alreadyOpen = false;
   }
   setTimeout(function() {
       newWin.onunload = newWinUnloadListener(true);
   }, 1000);

   popOutForAllForms();
}
function popOutForAllForms() {
  for(var i=0; i < document.forms.length; i++) {
    var form = document.forms[i];
    form.appendChild(createElementFromHTML("<input type='hidden' name='popOut' value='true' />"));
  }
}
function newWinUnloadListener(alreadyOpen) {
  return function() {
    this.opener.console.log("closing");
    if (!alreadyOpen) {
      this.opener.console.log("resetting");
      this.onunload = newWinUnloadListener(true);
      return;
    }
    this.opener.window.history.pushState({}, document.title, window.location.pathname);
    var forms = this.opener.window.document.forms;
    for(var i=0; i < forms.length; i++){
      var form = forms[i];
      form.removeChild(form.querySelector("input[name='popOut']"));
    }
  }
}

function initPopOut(imgpath) {
  console.log("init pop out");
  var popOutExists = (document.getElementById("orig_state_popOut").value == "true");
  if (popOutExists) {
    console.log("wut");
    popOut('/EntryApp/render-image', imgpath, true);
  }
}

function initIndexPage(popOutExists) {
  if (popOutExists) {
    var newWin = open("", "image");
    newWin.onunload = null;
    newWin = open("/static/waiting.html", "image");
    setTimeout(function () {
      newWin.onunload = newWinUnloadListener(true);
    }, 1000);
    popOutForAllForms();
  }
}
