import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_account_excel():
    # 设置下载目录
    download_dir = os.path.abspath("data/postingmanager")
    os.makedirs(download_dir, exist_ok=True)

    # ✅ Chrome 配置（增强版，绕过不安全下载提示）
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "profile.default_content_settings.popups": 0,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--safebrowsing-disable-download-protection")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-features=ChromeWhatsNewUI,DownloadBubble")
    # chrome_options.add_argument("--headless=new")  # 调试时可注释

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        print("⏳ 打开页面...")
        driver.get("http://14.136.114.138:7006")
        time.sleep(3)

        # 点击 Account
        print("⏳ 点击 Account...")
        account_button_xpath = "/html/body/gradio-app/div/main/div[1]/div/div/div[2]/div/div/button[2]"
        account_button = wait.until(EC.element_to_be_clickable((By.XPATH, account_button_xpath)))
        account_button.click()
        print("✅ 已点击 Account")

        # 点击 Refresh
        print("⏳ 点击 Refresh...")
        refresh_xpath = "/html/body/gradio-app/div/main/div[1]/div/div/div[4]/div/div[2]/div/div[1]/button[1]"
        refresh_button = wait.until(EC.element_to_be_clickable((By.XPATH, refresh_xpath)))
        time.sleep(1)
        refresh_button.click()
        print("✅ 已点击 Refresh")
        time.sleep(10)

        # 点击 Download Excel（通过按钮文本）
        print("⏳ 查找并点击 Download Excel 按钮...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "download excel" in btn.text.strip().lower():
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", btn)
                print("✅ 成功点击 Download Excel")
                break
        else:
            print("❌ 未找到包含 Download Excel 的按钮")

        # 等待下载完成
        time.sleep(20)

    except Exception as e:
        print(f"❌ 操作失败：{e}")

    finally:
        driver.quit()

    # 查找下载的 Excel 文件并重命名
    print("🔍 查找下载的 Excel 文件...")
    downloaded_files = [f for f in os.listdir(download_dir) if f.endswith(".xlsx")]
    if downloaded_files:
        latest_file = max([os.path.join(download_dir, f) for f in downloaded_files], key=os.path.getctime)
        today = datetime.today().strftime("%Y-%m-%d")
        new_filepath = os.path.join(download_dir, f"accounts_{today}.xlsx")
        os.rename(latest_file, new_filepath)
        print(f"✅ 下载完成并保存为：{new_filepath}")
    else:
        print("⚠️ 未找到下载的 Excel 文件，请确认是否触发下载或被拦截")

if __name__ == "__main__":
    fetch_account_excel()
