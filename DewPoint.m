% CONFIGURATION
channelID = YOUR_CHANNEL_ID;          
readAPIKey = 'YOUR_READ_API_KEY';     

% CONSTANTS for Magnus formula DEW Point calc.
a = 17.62;
b = 243.12;  % Celsius

% FETCH DATA (last 24 hours, adjust as needed)
data = thingSpeakRead(channelID, ...
    'NumPoints', 24, ...
    'Fields', [1,2], ...  % Field 1 = Temperature (°C), Field 2 = Humidity (%)
    'ReadKey', readAPIKey);

temperature = data(:,1);     % in °C
humidity = data(:,2);        % in %

% CALCULATE DEW POINT
alpha = log(humidity/100) + (a .* temperature) ./ (b + temperature);
dewPoint = (b .* alpha) ./ (a - alpha);

% FETCH TIMESTAMPS
timestamps = thingSpeakRead(channelID, 'NumPoints', 24, 'ReadKey', readAPIKey, 'OutputFormat', 'timetable');
time = timestamps.Timestamps;

% PLOT RESULTS
figure;
plot(time, temperature, '-o', 'DisplayName', 'Temperature (°C)');
hold on;
plot(time, dewPoint, '-x', 'DisplayName', 'Dew Point (°C)');
xlabel('Time');
ylabel('Temperature (°C)');
title('Temperature and Dew Point (Last 24 Hours)');
legend('show');
grid on;
xtickformat('HH:mm dd/MM');
xtickangle(45);

