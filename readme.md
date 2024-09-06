## API 文件：
1. 建立短網址 API

* URL: /shorten
* 方法: POST
* 輸入：
```json
{
  "original_url": "https://www.example.com/very/long/url"
}
```

成功回應 (201 Created)：
```json
{
  "short_url": "http://yourdomain.com/abc123",
  "expiration_date": 1625097600,
  "success": true
}
```

錯誤回應 (400 Bad Request)：

```json
{
  "success": false,
  "reason": "無效的 URL"
}
```
2. 重新導向 API

* URL: /<short_code>
* 方法: GET
* 行為：重新導向至原始 URL
錯誤回應 (404 Not Found)：
```json
{
  "success": false,
  "reason": "找不到短網址"
}
```

## 使用者指南：

1. 複製 GitHub ：
```bash
git clone https://github.com/ToooAir/short-url-system.git
cd short-url-system
```

2. 建立 Docker 映像檔：
```bash
docker build -t short-url-system .
```

3. 執行 Docker 容器：
```bash
docker run -p 8000:8000 -d short-url-system
```

4. 存取 API：

* 建立短網址：```curl -X POST -H "Content-Type: application/json" -d '{"original_url":"https://www.example.com/"}' http://127.0.0.1:8000/shorten```
* 使用短網址：在瀏覽器中訪問 ```http://127.0.0.1:8000/<short_code>```

5. 停止容器：
```bash
docker stop <container_id>
```

注意：請確保已安裝 Docker 且 Docker daemon 正在執行。