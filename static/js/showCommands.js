
async function showInterfaces() {
    try {
      const response = await fetch('/show_interfaces', {
        method: 'POST'
      });
      const result = await response.json();
      if (result) {
        const interfaces = result.interfaces;
        console.log(interfaces);
        addInterfaces(interfaces);
        showPorts();
        const newSwitchFace = document.getElementsByClassName('switch-face');
        const newSwitchRear = document.getElementsByClassName('switch-rear');
        const faceButton = document.getElementById('face-button');
        const rearButton = document.getElementById('rear-button');

        if (newSwitchFace.length > 0) {
          faceButton.style.display = 'block';
        };

        if (newSwitchRear.length > 0) {
          rearButton.style.display = 'block';
        };
      };

    } catch (error) {
      console.error('Error:', error);
    };
};

async function showRunningConfig() {
    const configButton = document.getElementById('running-config');
    const configOutput = document.getElementById('config-output');
    const vlanButton = document.getElementById('vlan-button');
    const vlanOutput = document.getElementById('vlan-output');
    try {
      const response = await fetch('/show_configuration', {
        method: 'POST'
      });
      const result = await response.json();
      if (result) {
        configOutput.textContent = result.running_config;
        configButton.style.display = 'block';
  
        for (const key in result.untagged_vlan) {
            if ((result.untagged_vlan).hasOwnProperty(key)) {
              if (interface_info[key]) {
                interface_info[key]['untagged_vlan'] = result.untagged_vlan[key]
              } else {
                interface_info[key] = {'untagged_vlan': result.untagged_vlan[key]}
              };
              const showVlans = document.createElement('p');
              showVlans.textContent = key + ' - Untagged:' + result.untagged_vlan[key];
              vlanOutput.appendChild(showVlans); 
            };
        };

        for (const key in result.tagged_vlan) {
            if ((result.tagged_vlan).hasOwnProperty(key)) {
              if (interface_info[key]) {
                interface_info[key]['tagged_vlan'] = result.tagged_vlan[key]
              } else {
                interface_info[key] = {'tagged_vlan': result.tagged_vlan[key]}
              };
              const showVlans = document.createElement('p');
              showVlans.textContent = key + ' - Tagged:' + result.tagged_vlan[key];
              vlanOutput.appendChild(showVlans); 
            };
        };

        console.log(interface_info)
        vlanButton.style.display = 'block';
      };
    } catch (error) {
      console.error('Error:', error);
    };
    showPorts();
};

async function showLldpNeighbors() {
    try {
      const response = await fetch('/show_lldp_neighbors', {
        method: 'POST'
      });
      const result = await response.json();
      if (result.lldp_neighbors) {
        console.log(result.lldp_neighbors)
        // const lldpNeighborsData = document.getElementById('lldp-neighbors-data');

        for (const port in result.lldp_neighbors) {
          if ((result.lldp_neighbors).hasOwnProperty(port)) {
            const listItem = document.createElement('textarea');
            const itemDetails = [];
            for (const key in result.lldp_neighbors[port]) {
              if (result.lldp_neighbors[port].hasOwnProperty(key)) {
                if (interface_info[port]) {
                  if (interface_info[port]['lldp_neighbors']) {
                    interface_info[port]['lldp_neighbors'][key] = result.lldp_neighbors[port][key]
                  } else {
                    interface_info[port]['lldp_neighbors'] = {key: result.lldp_neighbors[port][key]}
                  };
                } else {
                  interface_info[port] = {'lldp_neighbors': {key: result.lldp_neighbors[port][key]}};
                };
                itemDetails.push(`${key}: ${result.lldp_neighbors[port][key]}`);
              };
            };
            if ('lldp_neighbors' in interface_info[port]) {
              interface_info[port]['lldp_neighbors']['all_lines'] = itemDetails.join('\n'); 
            };
            // lldpNeighborsData.appendChild(listItem); 
          };
        };
      };
      showPorts();

    } catch (error) {
      console.error('Error:', error);
    };
    console.log(interface_info)
};

async function showCdpNeighbors() {
    try {
      const response = await fetch('/show_cdp_neighbors', {
        method: 'POST'
      });
      const result = await response.json();
      if (result) {
        console.log(result);
      };
    } catch (error) {
      console.error('Error:', error);
    };
};