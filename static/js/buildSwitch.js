function showPorts() {
  let portSlotInterfaces = []
  let currentPortSlot

  for (const portInfo in interface_info) {
    const splitPort = portInfo.split('/');
    const portSlot = splitPort[0]
    
    if (!currentPortSlot) {
      currentPortSlot = portSlot
      portSlotInterfaces.push(portInfo);
    } else if (currentPortSlot === portSlot) {
      portSlotInterfaces.push(portInfo)
    } else if (currentPortSlot !== portSlot ) {
      buildSwitch(currentPortSlot, portSlotInterfaces)
      portSlotInterfaces = []
      portSlotInterfaces.push(portInfo)
      currentPortSlot = portSlot
    };
  };
  if (currentPortSlot && portSlotInterfaces.length > 0) {
    buildSwitch(currentPortSlot, portSlotInterfaces)
  };
};

function buildSwitch(currentPortSlot, portSlotInterfaces) {

  const faceDropdown = document.getElementById('face-button-dropdown');
  const rearDropdown = document.getElementById('rear-button-dropdown');

  const visibleSwitchFace = document.getElementById('switch-face-' + currentPortSlot);
  const visibleSwitchRear = document.getElementById('switch-rear-' + currentPortSlot);

  if (visibleSwitchFace) {
    const parentElement = visibleSwitchFace.parentElement 
    parentElement.removeChild(visibleSwitchFace);
  };

  if (visibleSwitchRear) {
    const parentElement = visibleSwitchRear.parentElement 
    parentElement.removeChild(visibleSwitchRear);
  };

  const switchFace = document.createElement('div');
  switchFace.className = 'switch-face';
  switchFace.id = 'switch-face-' + currentPortSlot;

  const switchRear = document.createElement('div');
  switchRear.className = 'switch-rear';
  switchRear.id = 'switch-rear-' + currentPortSlot;

  const switchContainerOne = document.createElement('div');
  switchContainerOne.className = 'switch-container-one';

  const switchContainerTwo = document.createElement('div');
  switchContainerTwo.className = 'switch-container-two';

  const switchContainerThree = document.createElement('div');
  switchContainerThree.className = 'switch-container-three';

  const switchContainerFour = document.createElement('div');
  switchContainerFour.className = 'switch-container-four';

  const portsTopRow = document.createElement('div');
  portsTopRow.className = 'port-top-row';

  const portsBottomRow = document.createElement('div');
  portsBottomRow.className = 'port-bottom-row';

  for (let i = 0; i < portSlotInterfaces.length; i++) {
    const portInfo = portSlotInterfaces[i];
    const splitPort = portInfo.split('/');
    const portSlot = splitPort[0]
    const portSubSlot = splitPort[1]
    const portNumber = splitPort[2]
    if (interface_info[portInfo]['type'] === 'GbE') {
      const switchIsOdd = portNumber % 2 !== 0;
      const portButton = document.createElement('button');
      portButton.id = portInfo;
      portButton.type = "button";
      portButton.classList.add("network-port-button");
      portButton.setAttribute('onClick', 'showPortDetails(this)');

      let portUp = '';

      if ((interface_info[portInfo]['status']).toLowerCase() === 'up') {
        portUp = ' up';
      };

      let showPortNumber = `<div class="port-number">${portNumber}</div>`;

      if (interface_info[portInfo]['untagged_vlan']) {
        showPortNumber = `<div class="port-number untagged-vlan-${interface_info[portInfo]['untagged_vlan'][0]}">${portNumber}</div>`;
      };

      let portContacts = [
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`,
        `<span class="port-contact"></span>`
      ];

      if (interface_info[portInfo]['tagged_vlan']) {
        console.log('found tagged vlan' + interface_info[portInfo]['tagged_vlan'])
        if (portContacts.length >= (interface_info[portInfo]['tagged_vlan']).length > 0) {
          for (let i = 0; i < (interface_info[portInfo]['tagged_vlan']).length; i++) {
            portContacts[i] = `<span class="port-contact tagged-vlan-${interface_info[portInfo]['tagged_vlan'][i]}"></span>`;
          };
        } else {
          for (let i = 0; i < portContacts.length; i++) {
            portContacts[i] = `<span class="port-contact tagged-vlan-${interface_info[portInfo]['tagged_vlan'][i]}"></span>`;
          };
        };
      };

      let allPortContacts = portContacts.join('');

      if (switchIsOdd) {
        portButton.innerHTML = `
          <div class="port-lights-container">
            <div class="left-port-light-container">
              <span class="left-port-light${portUp}"></span>      
            </div>
            <div class="top-port-nub-container">
              <div class="left-port-light-nub"></div>
              <div class="right-port-light-nub"></div>
            </div>
            <div class="right-port-light-container">    
              <span class="right-port-light${portUp}"></span>     
            </div>
          </div>
          <div class="port-container">
            ${showPortNumber}
            <div class="port-contacts-container">
              ${allPortContacts}
            </div>
          </div>
        `
      } else {
        portButton.innerHTML = `
          <div class="port-container">
            <div class="port-contacts-container">
              ${allPortContacts}
            </div>
            ${showPortNumber}
          </div>
          <div class="port-lights-container">
            <div class="left-port-light-container">
              <span class="left-port-light${portUp}"></span>      
            </div>
            <div class="bottom-port-nub-container">
              <div class="left-port-light-nub"></div>
              <div class="right-port-light-nub"></div>
            </div>
            <div class="right-port-light-container">    
              <span class="right-port-light${portUp}"></span>     
            </div>
          </div>
        `
      };

      if (switchIsOdd) {
        portsTopRow.appendChild(portButton);
      } else {
        portsBottomRow.appendChild(portButton);
      };
    };
    if (interface_info[portInfo]['type'] === '10 GbE') {
      const portButton = document.createElement('button');
      portButton.id = portInfo;
      portButton.type = "button";
      portButton.classList.add("sfp-port-button");
      portButton.setAttribute('onClick', 'showPortDetails(this)');

      let showPortNumber = `<div class="sfp-port-number">${portNumber}</div>`

      if (interface_info[portInfo]['untagged_vlan']) {
        showPortNumber = `<div class="sfp-port-number untagged-vlan-${interface_info[portInfo]['untagged_vlan'][0]}">${portNumber}</div>`
      }

      let portContacts = [
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`,
        `<span class="sfp-port-contact"></span>`
      ]

      if (interface_info[portInfo]['tagged_vlan']) {
        if (portContacts.length >= (interface_info[portInfo]['tagged_vlan']).length > 0) {
          for (let i = 0; i < (interface_info[portInfo]['tagged_vlan']).length; i++) {
            portContacts[i] = `<span class="port-contact tagged-vlan-${interface_info[portInfo]['tagged_vlan'][i]}"></span>`
          };
        };
      };

      let allPortContacts = portContacts.join('');

      portButton.innerHTML = `
          <div class="sfp-port-container">
            ${showPortNumber}
            <div class="sfp-port-contacts-container">
              ${allPortContacts}
            </div>
            <div class="sfp-port-contacts-container">
              ${allPortContacts}
            </div>
          </div>
        `

      const dropdownMenu = document.createElement('div');
      dropdownMenu.id = portButton.id + `-dropdown`
      dropdownMenu.className = 'port-dropdown';

      const portOutput = document.createElement('div');
      portOutput.className = 'port-output';
      portOutput.textContent = interface_info[portInfo]['details'];

      dropdownMenu.appendChild(portOutput);
      portButton.appendChild(dropdownMenu);

      if (portSubSlot === '2') {
        switchContainerTwo.appendChild(portButton);
      } else if (portSubSlot === '3') {
        switchContainerThree.appendChild(portButton);
      } else if (portSubSlot === '4') {
        switchContainerFour.appendChild(portButton);
      } else {
        switchContainerTwo.appendChild(portButton);
      };
    };        
    if (interface_info[portInfo]['type'] === '40 GbE') {
      const portButton = document.createElement('button');
      portButton.id = portInfo;
      portButton.type = "button";
      portButton.classList.add("qsfp-port-button");
      portButton.setAttribute('onClick', 'showPortDetails(this)');

      let showPortNumber = `<div class="qsfp-port-number">${portNumber}</div>`

      if (interface_info[portInfo]['untagged_vlan']) {
        showPortNumber = `<div class="qsfp-port-number untagged-vlan-${interface_info[portInfo]['untagged_vlan'][0]}">${portNumber}</div>`
      }

      let portContacts = [
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`,
        `<span class="qsfp-port-contact"></span>`
      ]

      if (interface_info[portInfo]['tagged_vlan']) {
        if (portContacts.length >= (interface_info[portInfo]['tagged_vlan']).length > 0) {
          for (let i = 0; i < (interface_info[portInfo]['tagged_vlan']).length; i++) {
            portContacts[i] = `<span class="port-contact tagged-vlan-${interface_info[portInfo]['tagged_vlan'][i]}"></span>`
          };
        };
      };

      let allPortContacts = portContacts.join('');

      portButton.innerHTML = `
          <div class="qsfp-port-container">
            ${showPortNumber}
            <div class="qsfp-port-contacts-container">
              ${allPortContacts}
            </div>
            <div class="qsfp-port-contacts-container">
              ${allPortContacts}
            </div>
          </div>
        `

      const dropdownMenu = document.createElement('div');
      dropdownMenu.id = portButton.id + `-dropdown`
      dropdownMenu.className = 'port-dropdown';

      const portOutput = document.createElement('div');
      portOutput.className = 'port-output';
      portOutput.textContent = interface_info[portInfo]['details'];

      dropdownMenu.appendChild(portOutput);
      portButton.appendChild(dropdownMenu);

      if (portSubSlot === '2') {
        switchContainerTwo.appendChild(portButton);
      } else if (portSubSlot === '3') {
        switchContainerThree.appendChild(portButton);
      } else if (portSubSlot === '4') {
        switchContainerFour.appendChild(portButton);
      } else {
        switchContainerTwo.appendChild(portButton);
      };
    };
  };
  switchContainerOne.appendChild(portsTopRow);
  switchContainerOne.appendChild(portsBottomRow);
  switchFace.appendChild(switchContainerOne);
  switchFace.appendChild(switchContainerTwo);
  faceDropdown.appendChild(switchFace);
  if (switchContainerThree.childNodes.length > 0 || switchContainerFour.childNodes.length > 0) {
    switchRear.appendChild(switchContainerThree);
    switchRear.appendChild(switchContainerFour);
    rearDropdown.appendChild(switchRear);
  };
};