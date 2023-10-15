
const precursorEndline = [">", "#"];
const maxLineLength = 200;
let commandHistory = []
let history = 1
let interface_info = {}

const terminalButton = document.getElementById('terminal-button');
const terminal = document.getElementById('output-container');
const precursor = document.getElementById('precursor');
const inputField = document.getElementById('input');
const hostnameInput = document.getElementById('hostname');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const connectButton = document.getElementById('connect-button');
const showCommandButton = document.getElementById('show-command-button');
const hardware = document.getElementById('hardware');
const hardwareOutput = document.getElementById('hardware-output');
const software = document.getElementById('software');
const softwareOutput = document.getElementById('software-output');
const faceButton =  document.getElementById('face-button');
const rearButton = document.getElementById('rear-button');
const portDetailsDropdown = document.getElementById('port-details-dropdown');
const portDetailCurrentPort = document.getElementById('port-details-current-port');
const portDetailsOutput = document.getElementById('port-details-button-dropdown');
const portVlanOutput = document.getElementById('port-vlan-button-dropdown');
const portLldpOutput = document.getElementById('port-lldp-button-dropdown');

// focuses on the hostname input field when called
function focusOnInput() {
    inputField.focus();
  };

// prints output of user input commands to terminal window
function appendToTerminal(command, output) {
    const line = document.createElement("div");
    line.innerHTML = `<p class="terminal-output">${command}</p><p class="terminal-output">${output}</p>`;
    terminal.append(line);
  }

// builds or adds to the interface_info dictionary
function addInterfaces(interfaces) {
    for (const i in interfaces) {
        if (interface_info[interfaces[i]['port']]) {
        interface_info[interfaces[i]['port']]['status'] = interfaces[i]['status'];
        interface_info[interfaces[i]['port']]['type'] = interfaces[i]['type'];
        interface_info[interfaces[i]['port']]['details'] = interfaces[i]['details'];
        } else {
        interface_info[interfaces[i]['port']] = {
            'status': interfaces[i]['status'],
            'type': interfaces[i]['type'],
            'details': interfaces[i]['details']
        };
        };
    };
};

function toggleDropdown(dropdownButton) {
    const dropdownMenu = document.getElementById(dropdownButton.id + '-dropdown');

    if ((dropdownMenu.classList).contains('show-dropdown')) {
      dropdownMenu.classList.remove('show-dropdown');
      dropdownMenu.classList.add('hide');
      setTimeout(() => {
        dropdownMenu.classList.remove("hide");
      }, 500);
    } else {
      dropdownMenu.classList.add('show-dropdown');
    };
  };

function hideOtherDropdowns(button, dropdownClassName) {
  const classNameDropdowns = document.getElementsByClassName(dropdownClassName);

  for (const i in classNameDropdowns) {
    const foundDropdown = classNameDropdowns[i]
    if (foundDropdown.id && foundDropdown.id !== button.id + '-dropdown') {
      foundDropdown.classList.remove('show-dropdown');
    };
  };
};

function maxOutputLength(outputOverMax) {
  let newOutput = '';
  let lineLength = 0;

  for (let i = 0; i < outputOverMax.length; i++) {
    if (lineLength >= maxLineLength && outputOverMax[i] !== ' ') {
      newOutput += '\n'; 
      lineLength = 0;
    };
    newOutput += outputOverMax[i];
    lineLength++;
    if (outputOverMax[i] === '\n') {
      lineLength = 0;
    };
  };
  return newOutput;
};

function showPortDetails(button) {
  const portDetailsText = interface_info[button.id]['details']

  portDetailCurrentPort.textContent = button.id

  if (portDetailsText && (portDetailsDropdown.classList).contains('show-dropdown' ) && portDetailsText === portDetailsOutput.textContent) {
    portDetailsDropdown.classList.remove('show-dropdown');
    portDetailsDropdown.classList.add('hide');

    setTimeout(() => {
      portDetailsDropdown.classList.remove("hide");
    }, 500);

  } else {
    if (portDetailsText) {
      let portInfoOutput = portDetailsText
      if (portInfoOutput.length > maxLineLength) {
        portInfoOutput = maxOutputLength(portInfoOutput);
      };
      portDetailsOutput.innerHTML = portInfoOutput;
      portVlanOutput.innerHTML = '';
      portLldpOutput.innerHTML = ''; 
      if ('tagged_vlan' in interface_info[button.id] || 'untagged_vlan' in interface_info[button.id]) {
        let vlanOutput = '';
        if ('tagged_vlan' in interface_info[button.id]) {
          vlanOutput = 'Tagged Vlans: ' + interface_info[button.id]['tagged_vlan'];
        } 
        if ('untagged_vlan' in interface_info[button.id]) {
          vlanOutput = vlanOutput + '\nUntagged Vlans: ' + interface_info[button.id]['untagged_vlan'];
        };
        if (vlanOutput.length > maxLineLength) {
          vlanOutput = maxOutputLength(vlanOutput);
        };
        portVlanOutput.innerHTML = vlanOutput;
      };
      if ('lldp_neighbors' in interface_info[button.id]) {
        let lldpOutput = interface_info[button.id]['lldp_neighbors']['all_lines']
        if (lldpOutput.length > maxLineLength) {
          lldpOutput = maxOutputLength(lldpOutput);
        };
        portLldpOutput.innerHTML = lldpOutput;
      };
      portDetailsDropdown.classList.add('show-dropdown');
    };
  };
};


// collapses known hosts dropdowns when a host is selected and populates the hostname input field with IP address
function startSession(hostButton) {
    const splitHostButton = (hostButton.id).split('-')
    const hostname = splitHostButton[splitHostButton.length - 1]
    const visibleLocationDropdown = document.getElementsByClassName('location-dropdown');
    const visibleLocationGroupDropdown = document.getElementsByClassName('location-group-dropdown');
    const visibleHostnameButtonDropdown = document.getElementById('hostname-button-dropdown');

    hostnameInput.value = hostname;

    if (visibleLocationDropdown) {
        for (const i in visibleLocationDropdown) {
        const visibleLocation = document.getElementById((visibleLocationDropdown[i]).id);
        if (visibleLocation && (visibleLocation.classList).contains('show-dropdown')) {
            visibleLocation.classList.remove('show-dropdown');
        };
        };
    };
    if (visibleLocationGroupDropdown) {
        for (const i in visibleLocationGroupDropdown) {
        const visibleGroup = document.getElementById((visibleLocationGroupDropdown[i]).id);
        if (visibleGroup && (visibleGroup.classList).contains('show-dropdown')) {
            visibleGroup.classList.remove('show-dropdown');
        };
        };
    };
    visibleHostnameButtonDropdown.classList.remove('show-dropdown');
};

// gets known hosts from known_hosts.json and populates the known hosts dropdowns
const xhr = new XMLHttpRequest();
      xhr.open('GET', '/known_hosts', true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          const knownHosts = JSON.parse(xhr.responseText);
          const knownHostsDropdown = document.getElementById('hostname-button-dropdown');
          for (const locationGroup in knownHosts) {
            if (knownHosts.hasOwnProperty(locationGroup)) {
              const locationGroupContainer = document.createElement('div');

              const locationGroupButton = document.createElement('button');
              const locationGroupDropdown = document.createElement('div');

              locationGroupContainer.className = 'location-group-container';

              locationGroupButton.className = 'location-group';
              locationGroupButton.id = 'location-group-' + locationGroup;
              locationGroupButton.textContent = locationGroup;
              locationGroupButton.setAttribute('onclick', 'toggleDropdown(this)');

              locationGroupDropdown.className = 'location-group-dropdown';
              locationGroupDropdown.id = 'location-group-' + locationGroup + '-dropdown';

              locationGroupContainer.appendChild(locationGroupButton);
              locationGroupContainer.appendChild(locationGroupDropdown);
              knownHostsDropdown.appendChild(locationGroupContainer);

              for (const location in knownHosts[locationGroup]) {
                if (knownHosts[locationGroup].hasOwnProperty(location)) {

                  const locationContainer = document.createElement('div');
                  const locationButton = document.createElement('button');
                  const locationDropdown = document.createElement('div');

                  locationContainer.className = 'locations-container';

                  locationButton.className = 'location';
                  locationButton.id = 'location-group-' + locationGroup + '-' + location;
                  locationButton.textContent = location;
                  locationButton.setAttribute('onclick', 'toggleDropdown(this)');

                  locationDropdown.className = 'location-dropdown';
                  locationDropdown.id = 'location-group-' + locationGroup + '-' + location + '-dropdown';

                  locationContainer.appendChild(locationButton);
                  locationContainer.appendChild(locationDropdown);
                  locationGroupDropdown.appendChild(locationContainer);

                  for (const host in knownHosts[locationGroup][location]) {
                    if (knownHosts[locationGroup][location].hasOwnProperty(host)) {
                      const hostContainer = document.createElement('div');
                      const hostButton = document.createElement('button');

                      hostContainer.className = 'host-container';

                      hostButton.className = 'host';
                      hostButton.id = 'location-group-' + locationGroup + '-' + location + '-' + knownHosts[locationGroup][location][host];
                      hostButton.textContent = host;
                      hostButton.setAttribute('onclick', 'startSession(this)');

                      hostContainer.appendChild(hostButton);
                      locationDropdown.appendChild(hostContainer);
                    };
                  };
                };
              };
            };
          };
        };
      };
      xhr.send();


