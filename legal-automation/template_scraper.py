#!/usr/bin/env python3
"""
Government Template Web Scraper
Scrapes legal templates from court websites, government portals, and nonprofit resources
"""

import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    os.system("pip install beautifulsoup4")
    from bs4 import BeautifulSoup

try:
    import html2text
except ImportError:
    print("Installing html2text...")
    os.system("pip install html2text")
    import html2text


class GovernmentTemplateScraper:
    """Scrape and extract legal/government document templates"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = self.base_dir / 'legal-docs' / 'templates'
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Government and legal template sources
        self.template_sources = {
            'texas_courts': {
                'url': 'https://www.txcourts.gov/rules-forms/forms/',
                'description': 'Texas Supreme Court forms'
            },
            'harris_county': {
                'url': 'https://www.hcdistrictclerk.com/Common/e-filing/ef.aspx',
                'description': 'Harris County District Clerk forms'
            },
            'irs_forms': {
                'url': 'https://www.irs.gov/forms-instructions',
                'description': 'IRS tax-exempt forms'
            },
            'grants_gov': {
                'url': 'https://www.grants.gov/web/grants/forms.html',
                'description': 'Federal grant application forms'
            },
            'texas_procurement': {
                'url': 'https://comptroller.texas.gov/purchasing/publications/forms.php',
                'description': 'Texas procurement forms'
            }
        }

    def scrape_page(self, url: str, extract_links: bool = True) -> Dict[str, Any]:
        """
        Scrape a webpage and extract content

        Args:
            url: URL to scrape
            extract_links: Whether to extract download links

        Returns:
            Dictionary with scraped content
        """
        try:
            print(f"🔍 Scraping: {url}")

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract page title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'Untitled'

            # Extract all text content
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = True
            text_content = converter.handle(str(soup))

            # Extract form/PDF links
            links = []
            if extract_links:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if any(ext in href.lower() for ext in ['.pdf', '.docx', '.doc', '.xls']):
                        full_url = urljoin(url, href)
                        link_text = link.get_text().strip()
                        links.append({
                            'url': full_url,
                            'text': link_text,
                            'type': self._get_file_type(href)
                        })

            scraped_data = {
                'url': url,
                'title': title_text,
                'scraped_at': datetime.now().isoformat(),
                'text_content': text_content,
                'document_links': links,
                'link_count': len(links)
            }

            print(f"✅ Scraped: {title_text} ({len(links)} document links found)")

            return scraped_data

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return {'url': url, 'error': str(e)}

    def _get_file_type(self, filename: str) -> str:
        """Extract file type from filename"""
        if '.pdf' in filename.lower():
            return 'PDF'
        elif '.docx' in filename.lower() or '.doc' in filename.lower():
            return 'Word'
        elif '.xlsx' in filename.lower() or '.xls' in filename.lower():
            return 'Excel'
        return 'Unknown'

    def download_template(self, url: str, filename: str = None) -> Path:
        """
        Download template file

        Args:
            url: URL of template to download
            filename: Optional custom filename

        Returns:
            Path to downloaded file
        """
        try:
            if filename is None:
                filename = os.path.basename(urlparse(url).path)

            output_path = self.templates_dir / filename

            print(f"📥 Downloading: {filename}")

            response = requests.get(url, headers=self.headers, stream=True, timeout=60)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ Downloaded: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            return None

    def scrape_all_sources(self) -> Dict[str, Any]:
        """
        Scrape all configured template sources

        Returns:
            Dictionary with all scraped data
        """
        results = {
            'scrape_timestamp': datetime.now().isoformat(),
            'sources_scraped': len(self.template_sources),
            'sources': {}
        }

        for source_key, source_info in self.template_sources.items():
            print(f"\n{'='*60}")
            print(f"Scraping: {source_info['description']}")
            print(f"{'='*60}")

            scraped = self.scrape_page(source_info['url'])
            results['sources'][source_key] = scraped

        # Save results
        results_file = self.templates_dir / f"scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Scrape results saved: {results_file}")

        return results

    def download_all_documents(self, scraped_data: Dict[str, Any], max_per_source: int = 10) -> List[Path]:
        """
        Download all documents from scrape results

        Args:
            scraped_data: Results from scrape_all_sources()
            max_per_source: Maximum documents to download per source

        Returns:
            List of downloaded file paths
        """
        downloaded_files = []

        for source_key, source_data in scraped_data.get('sources', {}).items():
            if 'error' in source_data:
                continue

            links = source_data.get('document_links', [])[:max_per_source]

            print(f"\n📥 Downloading from {source_key} ({len(links)} files)")

            for link in links:
                path = self.download_template(link['url'])
                if path:
                    downloaded_files.append(path)

        print(f"\n✅ Total downloaded: {len(downloaded_files)} files")
        return downloaded_files

    def extract_html_template_code(self, url: str) -> str:
        """
        Extract HTML/CSS code from a webpage for template creation

        Args:
            url: URL of page to extract

        Returns:
            HTML source code
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Prettify the HTML
            html_code = soup.prettify()

            # Save to file
            filename = f"template_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            output_path = self.templates_dir / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_code)

            print(f"✅ HTML template code saved: {output_path}")

            return html_code

        except Exception as e:
            print(f"❌ Error extracting HTML: {e}")
            return ""

    def search_form_by_keyword(
        self,
        keyword: str,
        search_engines: List[str] = None
    ) -> List[Dict[str, str]]:
        """
        Search for government forms by keyword

        Args:
            keyword: Search keyword (e.g., "Form 1023", "opioid grant")
            search_engines: List of engines to search

        Returns:
            List of search results
        """
        if search_engines is None:
            search_engines = ['google']

        results = []

        # Construct search queries
        search_queries = [
            f"{keyword} site:irs.gov filetype:pdf",
            f"{keyword} site:texas.gov filetype:pdf",
            f"{keyword} site:grants.gov filetype:pdf",
            f"{keyword} government form filetype:pdf"
        ]

        print(f"🔍 Searching for: {keyword}")

        for query in search_queries:
            # Note: Actual web search would require API keys (Google Custom Search, etc.)
            # For now, we'll return placeholder structure
            results.append({
                'query': query,
                'engine': 'google',
                'note': 'Implement with Google Custom Search API or similar'
            })

        return results

    def create_template_from_scrape(
        self,
        source_html: str,
        template_name: str,
        variables: List[str]
    ) -> Path:
        """
        Create a template file with placeholders from scraped HTML

        Args:
            source_html: Source HTML content
            template_name: Name for the template
            variables: List of variable names to replace

        Returns:
            Path to created template
        """
        template_content = source_html

        # Replace specific text with variables
        for var in variables:
            # Create placeholder syntax {{variable_name}}
            placeholder = f"{{{{{var}}}}}"
            # You would implement specific text replacement logic here
            template_content = template_content.replace(var, placeholder)

        # Save template
        template_file = self.templates_dir / f"{template_name}.html"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)

        print(f"✅ Template created: {template_file}")

        return template_file


class SpecificFormScraper:
    """Scraper for specific government forms"""

    @staticmethod
    def scrape_texas_cybersecurity_grant_info() -> Dict[str, Any]:
        """Scrape Texas DIR cybersecurity grant information"""
        url = 'https://dir.texas.gov/cybersecurity'

        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            info = {
                'url': url,
                'title': soup.find('title').get_text() if soup.find('title') else 'Texas Cybersecurity',
                'links': []
            }

            # Find all links with 'grant' or 'funding' in text
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                if 'grant' in link_text or 'funding' in link_text or 'cyber' in link_text:
                    info['links'].append({
                        'url': urljoin(url, link['href']),
                        'text': link.get_text().strip()
                    })

            return info

        except Exception as e:
            print(f"❌ Error scraping Texas cybersecurity info: {e}")
            return {'error': str(e)}

    @staticmethod
    def scrape_texas_opioid_grant_info() -> Dict[str, Any]:
        """Scrape Texas Opioid Abatement Fund Council information"""
        url = 'https://www.texasopioidcouncil.org/'

        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            info = {
                'url': url,
                'title': soup.find('title').get_text() if soup.find('title') else 'Texas Opioid Council',
                'application_links': []
            }

            # Find application/grant links
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                if any(keyword in link_text for keyword in ['application', 'grant', 'funding', 'form']):
                    info['application_links'].append({
                        'url': urljoin(url, link['href']),
                        'text': link.get_text().strip()
                    })

            return info

        except Exception as e:
            print(f"❌ Error scraping Texas opioid grant info: {e}")
            return {'error': str(e)}


def main():
    """Main execution for testing"""
    print("="*70)
    print("GOVERNMENT TEMPLATE WEB SCRAPER")
    print("="*70)
    print()

    scraper = GovernmentTemplateScraper()

    # Test 1: Scrape all template sources
    print("\n--- Test 1: Scrape All Template Sources ---")
    results = scraper.scrape_all_sources()

    # Test 2: Extract template code from a specific page
    print("\n--- Test 2: Extract HTML Template Code ---")
    # Example: scraper.extract_html_template_code('https://www.txcourts.gov/rules-forms/forms/')

    # Test 3: Search for specific forms
    print("\n--- Test 3: Search for Forms ---")
    scraper.search_form_by_keyword("Form 1023")
    scraper.search_form_by_keyword("opioid grant application")

    # Test 4: Scrape specific grant information
    print("\n--- Test 4: Scrape Grant Information ---")
    cyber_info = SpecificFormScraper.scrape_texas_cybersecurity_grant_info()
    opioid_info = SpecificFormScraper.scrape_texas_opioid_grant_info()

    print(f"\nCybersecurity Grant Links Found: {len(cyber_info.get('links', []))}")
    print(f"Opioid Grant Links Found: {len(opioid_info.get('application_links', []))}")

    # Test 5: Download documents (COMMENTED - uncomment when ready)
    # print("\n--- Test 5: Download Templates ---")
    # scraper.download_all_documents(results, max_per_source=3)

    print("\n" + "="*70)
    print("✅ Template scraping test complete!")
    print(f"Templates directory: {scraper.templates_dir}")
    print("="*70)


if __name__ == '__main__':
    main()
