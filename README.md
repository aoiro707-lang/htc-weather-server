# HTC Weather Server

Server Flask thay thế HTC Weather, trả dữ liệu từ OpenWeatherMap.

## Deploy nhanh trên Render
1. Fork repo này về GitHub cá nhân của bạn.
2. Vào [Render](https://render.com), chọn "New Web Service".
3. Kết nối với repo này, chọn branch `main`.
4. Render sẽ build và cấp cho bạn 1 URL, ví dụ:
   ```
   https://htc-weather-server.onrender.com
   ```

## Registry cho HTC HD2
Vào registry:
```
HKEY_CURRENT_USER\Software\HTC\Manila
```

Tạo/chỉnh 2 string:
```
Weather.ServerURLGeoCodeOverride = https://<your-app>.onrender.com/getweather?lat=%s&lon=%s
Weather.ServerURLOverride        = https://<your-app>.onrender.com/getstaticweather?locCode=%ls
```

Restart máy → mở Weather widget → sẽ tự lấy dữ liệu từ server Render.
