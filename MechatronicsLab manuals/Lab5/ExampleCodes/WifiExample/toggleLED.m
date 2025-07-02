function toggleLED
    % toggleLED.mlx
    % ---------------------------------------------------------------------
    % Example MATLAB script to connect to the Arduino Nano ESP32 (Alvik
    % robot) over TCP, send LED toggles with \r\n, and read incoming data
    % in the background using a callback.
    %
    % This version uses "configureTerminator" and "configureCallback"
    % to handle the reading of data line-by-line in MATLAB versions where
    % direct property assignment (e.g., t.Terminator = 'LF') is not allowed.
    %
    % REQUIREMENTS:
    % - MATLAB R2019b or later, but some versions only allow setting
    %   terminator/callback via these functions.
    % - Arduino Nano ESP32 running the non-blocking server code.

    % Clear workspace and command window (optional):
    clearvars; clc;

    % 1) Define the IP address and port of your Arduino Nano ESP32:
    arduinoIP   = '192.168.0.101';  % <-- Replace if needed
    arduinoPort = 5050;               % <-- Must match TCP_PORT in Arduino code

    % 2) Create a tcpclient object to connect to the Arduino.
    %    'Timeout' is how long MATLAB will wait for a response.
    try
        t = tcpclient(arduinoIP, arduinoPort, 'Timeout', 5);
        disp('Connected to Arduino Nano ESP32 via TCP.');
    catch ME
        warning('Failed to connect: %s', ME.message);
        return;
    end

    % 3) Configure the tcpclient object to read data in the background:
    %    We'll treat '\n' (LF) as the line terminator. Each time a full line
    %    is received, the callback "onBytesAvailable" is triggered.

    % -- Set the terminator to LF (so it triggers on '\n'):
    configureTerminator(t, "LF");

    % -- Configure the callback to fire upon "terminator":
    configureCallback(t, "terminator", @onBytesAvailable);

    % 4) Example toggling loop:
    %    We send "1\r\n" to turn the LED on, then "0\r\n" to turn it off, each second.
    numToggles = 10;  % number of toggles (on+off steps)
    for i = 1:numToggles
        % Turn LEDs on (green)
        write(t, "1", "string");  % Now we send "1\r\n"
        fprintf('Sent: 1 (LED ON)\n');
        pause(2);
    
        % Turn LEDs off
        write(t, "0", "string");  % Now we send "0\r\n"
        fprintf('Sent: 0 (LED OFF)\n');
        pause(2);
    end

    % 5) (Optional) read any leftover data in the buffer:
    if t.NumBytesAvailable > 0
        leftoverData = read(t, t.NumBytesAvailable, "uint8");
        disp("Leftover data from Arduino: " + string(char(leftoverData)));
    end

    % 6) Close the connection (tcpclient object is closed when cleared)
    clear t
    disp('Connection closed.');
end



function onBytesAvailable(src, ~)
    % onBytesAvailable is the callback that runs in the background
    % whenever a full line of data (per 'Terminator' = LF) arrives.
    %
    % NOTE: The second argument (~) is the event data, which we don't need here.

    % Read all available bytes as a string
    data = read(src, src.BytesAvailable, "uint8");
    strData = string(char(data));

    % If multiple lines arrived at once, split them by newline:
    lines = strsplit(strData, newline);

    for i = 1:length(lines)
        thisLine = strtrim(lines{i});
        if ~isempty(thisLine)
            fprintf("Received [BG]: %s\n", thisLine);
        end
    end
end

