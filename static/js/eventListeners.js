

hostnameInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
    connectButton.click();
    inputField.focus();
    }
});

usernameInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        connectButton.click();
        inputField.focus();
    }
});

passwordInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        connectButton.click();
        inputField.focus();
    }
});

connectButton.addEventListener('click', async () => {
    const hostname = hostnameInput.value;
    const username = usernameInput.value;
    const password = passwordInput.value;

    const response = await fetch('/connect', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        hostname: hostname,
        username: username,
        password: password
    })
    });
    const result = await response.json();
    precursor.textContent = result.precursor;
    inputField.value = " ";
    hardware.textContent = result.hardware;
    // hardwareOutput.setAttribute('src', result.data_sheet);
    software.textContent = result.software;
    // softwareOutput.setAttribute('src', result.cli_reference);

    showCommandButton.style.display = 'block';
    terminalButton.style.display = 'block';

    usernameInput.style.display = 'none';
    passwordInput.style.display = 'none';
    connectButton.style.display = 'none';
});

faceButton.addEventListener('click', () => {
  hideOtherDropdowns(faceButton, 'port-details-dropdown');
});

rearButton.addEventListener('click', () => {
  hideOtherDropdowns(rearButton, 'port-details-dropdown');
});


// terminal event listener
inputField.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
      const command = inputField.value;
      commandHistory.push(command)
      try {
        const response = await fetch('/send-command', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            command: command
          })
        });
        const result = await response.json();
        let precursorCommand
        if (result) {
          if (precursor.textContent) {
            precursorCommand = precursor.textContent + command;
          } else {
            precursorCommand = result.precursor + command;
          };

          const endline = new RegExp("(" + precursorEndline.join("|") + ")(.*)");
          const endlineResult = result.precursor.split(endline);
          if (endlineResult.length > 2) {
            precursor.textContent = endlineResult[0] + endlineResult[1];
            inputField.value = endlineResult[2];
          } else {
            precursor.textContent = result.precursor;
            inputField.value = " ";
          };
          appendToTerminal(precursorCommand, result.output || result.error);
          terminal.scrollTop = terminal.scrollHeight;
        }
      } catch (error) {
        console.error('Error:', error);
      }
    }

    if (event.key === "ArrowUp") {
      console.log('arrow up pressed')
      console.log('command history length: ' + commandHistory.length)
      console.log('history: ' + history)
      console.log(commandHistory)
    }

    if (event.key === "ArrowUp" && commandHistory.length >= history) {
      inputField.value = commandHistory[commandHistory.length - history] + ' '
      history += 1
    };

    if (event.key === "ArrowDown" && history > 1) {
      history -= 1
      inputField.value = commandHistory[commandHistory.length - (history - 1)] + ' '
    };

    if (event.key === "ArrowDown" && history === 1) {
      inputField.value = " ";
    };
  });
