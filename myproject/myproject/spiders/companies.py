import scrapy
import re
from urllib.parse import urlparse, urljoin
from pathlib import Path

class CompaniesSpider(scrapy.Spider):
    name = "companies"
    
    # Başlangıç URL'lerini belirleyin
    start_urls = [
        "https://www.wiki.com.tr/",
        "https://www.sailteknoloji.com/?srsltid=AfmBOorhUnjbf0QXzQvz5GsKzJyUPTGvSj1i2SEhgauQV8eIX_YWX8YM",
    ]

    def parse(self, response):
        # Sayfanın HTML içeriğini al
        html_content = response.text
        
        # E-posta adresi bulmak için regex kullan
        email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_regex, html_content)

        # Bulunan e-posta adreslerini yazdır
        if emails:
            for email in emails:
                self.log(f"Bulunan e-posta: {email}")
        else:
            self.log("E-posta adresi bulunamadı.")

        # İletişim formunu bulmak için
        forms = response.css('form')
        if forms:
            for form in forms:
                action = form.css('::attr(action)').get()
                self.log(f"Form action: {action}")
                form_html = form.get()
                self.log(f"Form HTML: {form_html[:1000]}")  # Uzun HTML içeriğini sınırlı şekilde yazdırmak
        else:
            self.log("İletişim formu bulunamadı.")

        # Sayfanın URL'sine göre dosya adı belirle
        domain = urlparse(response.url).netloc
        filename = f"companies-{domain}.html"
        
        # Sayfanın içeriğini dosyaya yaz
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        # Diğer sayfalara erişmek için bağlantıları takip et
        links = response.css('a::attr(href)').getall()
        for link in links:
            next_page_url = urljoin(response.url, link)
            if self.is_valid_page(next_page_url):
                self.log(f"Next page: {next_page_url}")
                yield scrapy.Request(next_page_url, callback=self.parse)

    def is_valid_page(self, url):
        """
        Geçerli sayfa URL'sini kontrol eder.
        """
        parsed_url = urlparse(url)
        # Sadece geçerli alan adındaki sayfalara gidilmesini sağlar
        return parsed_url.netloc in [urlparse(start_url).netloc for start_url in self.start_urls]
