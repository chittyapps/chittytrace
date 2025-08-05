import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import asyncio

from claude_integration import ClaudeAnalyzer


class PackageGenerator:
    def __init__(self, analyzer: ClaudeAnalyzer):
        self.analyzer = analyzer
        self.output_dir = Path("generated_packages")
        self.output_dir.mkdir(exist_ok=True)
        
        # Cook County specific formatting requirements
        self.cook_county_requirements = {
            "exhibit_numbering": "sequential",  # Exhibit 1, Exhibit 2, etc.
            "page_size": "8.5x11",
            "margins": "1 inch all sides",
            "font": "Times New Roman or Arial",
            "font_size": "12pt",
            "line_spacing": "double",
            "exhibit_sticker": {
                "position": "bottom right",
                "content": ["Exhibit Number", "Case Number", "Date"]
            },
            "cover_sheet": True,
            "index_required": True,
            "authentication": "notarized affidavit required"
        }
    
    async def generate_court_exhibit(self, 
                                   document_path: str,
                                   exhibit_number: int,
                                   case_info: Dict[str, str]) -> Dict[str, Any]:
        """Generate a court-ready exhibit with Cook County formatting"""
        
        exhibit_data = {
            "exhibit_number": exhibit_number,
            "case_number": case_info.get("case_number"),
            "case_caption": case_info.get("caption"),
            "date_marked": datetime.now().strftime("%B %d, %Y"),
            "document_path": document_path,
            "authentication": {
                "type": "affidavit",
                "affiant": case_info.get("affiant"),
                "notary_required": True
            }
        }
        
        # Generate exhibit cover sheet
        cover_sheet = await self._generate_cover_sheet(exhibit_data)
        
        # Generate authentication affidavit
        affidavit = await self._generate_authentication_affidavit(exhibit_data)
        
        return {
            "exhibit_data": exhibit_data,
            "cover_sheet": cover_sheet,
            "affidavit": affidavit,
            "formatting_requirements": self.cook_county_requirements
        }
    
    async def generate_exhibit_package(self,
                                     documents: List[Dict[str, Any]],
                                     case_info: Dict[str, str],
                                     purpose: str) -> Dict[str, Any]:
        """Generate complete exhibit package for Cook County court filing"""
        
        package = {
            "case_info": case_info,
            "purpose": purpose,
            "created_date": datetime.now().isoformat(),
            "exhibits": [],
            "index": [],
            "cover_letter": "",
            "certificate_of_service": ""
        }
        
        # Generate exhibits
        for idx, doc in enumerate(documents, 1):
            exhibit = await self.generate_court_exhibit(
                doc["path"],
                idx,
                case_info
            )
            package["exhibits"].append(exhibit)
            package["index"].append({
                "exhibit_number": idx,
                "description": doc.get("description", ""),
                "pages": doc.get("pages", "")
            })
        
        # Generate package components
        package["cover_letter"] = await self._generate_cover_letter(package)
        package["certificate_of_service"] = await self._generate_certificate_of_service(case_info)
        package["table_of_contents"] = await self._generate_table_of_contents(package["index"])
        
        # Save package
        package_path = self._save_package(package)
        package["saved_path"] = str(package_path)
        
        return package
    
    async def _generate_cover_sheet(self, exhibit_data: Dict[str, Any]) -> str:
        """Generate exhibit cover sheet per Cook County requirements"""
        
        prompt = f"""Generate a formal exhibit cover sheet for Cook County court with:
        
        Case Caption: {exhibit_data['case_caption']}
        Case Number: {exhibit_data['case_number']}
        Exhibit Number: {exhibit_data['exhibit_number']}
        Date: {exhibit_data['date_marked']}
        
        Format according to Cook County Circuit Court requirements."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return response.content
    
    async def _generate_authentication_affidavit(self, exhibit_data: Dict[str, Any]) -> str:
        """Generate authentication affidavit for exhibit"""
        
        prompt = f"""Generate a formal authentication affidavit for court exhibit:
        
        Affiant: {exhibit_data['authentication']['affiant']}
        Exhibit Number: {exhibit_data['exhibit_number']}
        Case: {exhibit_data['case_caption']}
        
        Include:
        1. Affiant's personal knowledge
        2. Description of document
        3. Statement of authenticity
        4. Notary section
        
        Format for Cook County Circuit Court."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return response.content
    
    async def _generate_cover_letter(self, package: Dict[str, Any]) -> str:
        """Generate cover letter for exhibit package"""
        
        prompt = f"""Generate a formal cover letter for court exhibit package submission:
        
        Case: {package['case_info']['caption']}
        Number of Exhibits: {len(package['exhibits'])}
        Purpose: {package['purpose']}
        
        Include professional formatting and all required elements."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return response.content
    
    async def _generate_certificate_of_service(self, case_info: Dict[str, str]) -> str:
        """Generate certificate of service"""
        
        prompt = f"""Generate a certificate of service for:
        
        Case: {case_info['caption']}
        Parties: {case_info.get('parties', [])}
        
        Include all required elements for Cook County filing."""
        
        response = await self.analyzer.chat_model.ainvoke([
            {"role": "user", "content": prompt}
        ])
        
        return response.content
    
    async def _generate_table_of_contents(self, index: List[Dict[str, Any]]) -> str:
        """Generate table of contents for exhibit package"""
        
        toc = "TABLE OF CONTENTS\n\n"
        toc += "Exhibit No.\tDescription\t\t\tPages\n"
        toc += "-" * 60 + "\n"
        
        for item in index:
            toc += f"{item['exhibit_number']}\t\t{item['description'][:40]}\t\t{item['pages']}\n"
        
        return toc
    
    def _save_package(self, package: Dict[str, Any]) -> Path:
        """Save exhibit package to disk"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_number = package['case_info']['case_number'].replace(" ", "_")
        package_name = f"exhibit_package_{case_number}_{timestamp}"
        package_path = self.output_dir / package_name
        package_path.mkdir(exist_ok=True)
        
        # Save package metadata
        with open(package_path / "package_metadata.json", "w") as f:
            json.dump(package, f, indent=2, default=str)
        
        # Save individual components
        with open(package_path / "cover_letter.txt", "w") as f:
            f.write(package["cover_letter"])
        
        with open(package_path / "table_of_contents.txt", "w") as f:
            f.write(package["table_of_contents"])
        
        with open(package_path / "certificate_of_service.txt", "w") as f:
            f.write(package["certificate_of_service"])
        
        # Create exhibit subdirectories
        for idx, exhibit in enumerate(package["exhibits"], 1):
            exhibit_dir = package_path / f"Exhibit_{idx}"
            exhibit_dir.mkdir(exist_ok=True)
            
            with open(exhibit_dir / "cover_sheet.txt", "w") as f:
                f.write(exhibit["cover_sheet"])
            
            with open(exhibit_dir / "authentication_affidavit.txt", "w") as f:
                f.write(exhibit["affidavit"])
        
        return package_path