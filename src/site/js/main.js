const LIGHT_ON = true;
const LIGHT_OFF = false;

const AUTO_ENABLED = true;
const AUTO_DISABLED = false;

const ENABLED = true;
const DISABLED = false;

var lastRequestStatus = null;
var globalInfo = {soilHumidity: null, ambientLightStatus: null, warningCodes: null, growthLampStatus: null, powerDrawData: null, autocontrolStatus: null};

var debug = false;

var dataChartConfig = {
    type: "line"
}

// var dataChart = new Chart(document.getElementById("infograph-chart").getContext("2d"), dataChartConfig)

function genWarningString() {
    if(globalInfo.warningCodes!=null) {
        camStatus=(globalInfo.warningCodes.camera ? "enabled":"disabled");
        contStatus=(globalInfo.warningCodes.controller ? "enabled":"disabled");
        return `Camera is ${camStatus}<br>Controller is ${contStatus}`;
    }
}

function warnCameraMalfunction() {
    displayModal("The camera subsystem is disabled.");
}

function warnControllerMalfunction() {
    displayModal("The controller subsystem is disabled.");
}

function updatePageContent() {
    
    // updates page content from global info
    // can be used to perform sanity checks following button clicks
    
    // set soil humidity if value is set
    if(globalInfo.soilHumidity != null) {
        document.getElementById("soil-humidity-percentage").innerHTML=globalInfo.soilHumidity.toString()+"%";
    }

    // set ambient lighting card status if value is set
    // light off = "Turn On"
    // light on = "Turn Off"
    if(globalInfo.ambientLightStatus == LIGHT_ON) {
        document.getElementById("ambient-lighting-toggle").innerHTML = "Turn Off";
    } else if(globalInfo.ambientLightStatus == LIGHT_OFF) {
        document.getElementById("ambient-lighting-toggle").innerHTML = "Turn On";
    } else {
        // return to "No Connection"
        document.getElementById("ambient-lighting-toggle").innerHTML = "No Connection";
    }

    // PLACE WARNING INFORMATION CODE HERE
    document.getElementById("warning-string").innerHTML=genWarningString();

    // set growth lamp status if value is set
    if(globalInfo.growthLampStatus == LIGHT_ON) {
        document.getElementById("growth-lamp-toggle").innerHTML = "Turn Off";
    } else if(globalInfo.growthLampStatus == LIGHT_OFF) {
        document.getElementById("growth-lamp-toggle").innerHTML = "Turn On";
    } else {
        // return to "No Connection"
        document.getElementById("growth-lamp-toggle").innerHTML = "No Connection";
    }

    // PLACE POWER DRAW CODE HERE
    // Power draw information definitions required

    // set autocontrol status if value is set
    if(globalInfo.autocontrolStatus == AUTO_ENABLED) {
        document.getElementById("autocontrol-toggle").innerHTML = "Disable Autocontrol";
    } else if(globalInfo.autocontrolStatus == AUTO_DISABLED) {
        document.getElementById("autocontrol-toggle").innerHTML = "Enable Autocontrol";
    } else {
        // return to "No Connection"
        document.getElementById("autocontrol-toggle").innerHTML = "No Connection";
    }
}

function httpRequestCallback() {
    
    // check for correct request
    lastRequestStatus = this.status;
    
    var parsedResponse;

    // parse JSON response if correct
    if(this.readyState==4 && this.status==200) {
        parsedResponse=JSON.parse(this.responseText);

        // attempt to set global data
        // check for null response
        if(parsedResponse!=null) {
            // access parsed elements
            if(parsedResponse.soilHumidity!=null) globalInfo.soilHumidity=parsedResponse.soilHumidity;
            if(parsedResponse.ambientLightStatus!=null) globalInfo.ambientLightStatus=parsedResponse.ambientLightStatus;
            if(parsedResponse.warningCodes!=null) globalInfo.warningCodes=parsedResponse.warningCodes;
            if(parsedResponse.growthLampStatus!=null) globalInfo.growthLampStatus=parsedResponse.growthLampStatus;
            if(parsedResponse.powerDrawData!=null) globalInfo.powerDrawData=parsedResponse.powerDrawData;
            if(parsedResponse.autocontrolStatus!=null) globalInfo.autocontrolStatus=parsedResponse.autocontrolStatus;

        }
    }
    
    updatePageContent();
}

function updateHabitatImage() {
    // block browser image caching
    // new image is captured per HTTP GET request
    document.getElementById("recent-habitat-image").src="/habview#"+new Date().getTime().toString();
}

// create HTTP request object and attach callback function
var httpObject = new XMLHttpRequest();
httpObject.onreadystatechange = httpRequestCallback;

function fetchFullUpdate() {
    // fetch application global info
    httpObject.open("GET", "/info", true);
    httpObject.send();
}

function sendActionCmd(command, subsystem, state) {
    // assemble JSON packet and send request asynchronously
    httpObject.open("POST", "/action", true);
    httpObject.setRequestHeader("Content-type","application/json")
    
    if(debug) mode="normal";
    if(!debug) mode="debug";

    httpObject.send(JSON.stringify({mode:"normal",command:command,subsystem:subsystem,state:state}));
}

window.onload=function() {
    // attach command click events
    document.getElementById("ambient-lighting-toggle").onclick=function() {
        if(globalInfo.warningCodes.controller==DISABLED) {
            warnControllerMalfunction();
            return;
        }

        if(globalInfo.ambientLightingStatus==LIGHT_ON) {
            sendActionCmd("set", "ambientlighting", false);
        } else if(globalInfo.ambientLightingStatus==LIGHT_OFF) {
            sendActionCmd("set", "ambientlighting", true);
        }
    };

    document.getElementById("growth-lamp-toggle").onclick=function() {
        if(globalInfo.warningCodes.controller==DISABLED) {
            warnControllerMalfunction();
            return;
        }

        if(globalInfo.growthLampStatus==LIGHT_ON) {
            sendActionCmd("set", "growthlamp", false);
        } else if(globalInfo.growthLampStatus==LIGHT_OFF) {
            sendActionCmd("set", "growthlamp", true);
        }
    };

    document.getElementById("autocontrol-toggle").onclick=function() {
        if(globalInfo.autocontrolStatus==AUTO_ENABLED) {
            sendActionCmd("set", "autocontrol", false);
        } else if(globalInfo.autocontrolStatus==AUTO_DISABLED) {
            sendActionCmd("set", "autocontrol", true);
        }
    };

    // refresh page content on 1,000ms interval
    window.setInterval(fetchFullUpdate,1000);
}
