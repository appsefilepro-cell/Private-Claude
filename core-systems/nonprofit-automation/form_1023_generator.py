#!/usr/bin/env python3
"""
IRS Form 1023 / 1023-EZ Generator
Automated 501(c)(3) Tax-Exempt Application
"""

import os
import json
from datetime import datetime
from typing import Dict, Any


class Form1023Generator:
    """Generates IRS Form 1023 and 1023-EZ for 501(c)(3) status"""

    def __init__(self):
        self.output_dir = "core-systems/nonprofit-automation/output"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_form_1023_ez(self, org_info: Dict[str, Any]) -> str:
        """
        Generate Form 1023-EZ (Streamlined Application)

        Eligibility:
        - Gross receipts ≤ $50,000/year (averaged over 3 years)
        - Assets ≤ $250,000
        - Fee: $275
        """

        content = f"""
╔══════════════════════════════════════════════════════════════╗
║         IRS FORM 1023-EZ - STREAMLINED APPLICATION           ║
║         Application for Recognition of Exemption             ║
║         Under Section 501(c)(3) of the Internal Revenue Code ║
╚══════════════════════════════════════════════════════════════╝

Form 1023-EZ
(Rev. January 2024)
Department of the Treasury
Internal Revenue Service

Streamlined Application for Recognition of Exemption
Under Section 501(c)(3) of the Internal Revenue Code

OMB No. 1545-0056

═══════════════════════════════════════════════════════════════
PART I - IDENTIFICATION OF APPLICANT
═══════════════════════════════════════════════════════════════

1. Full Name of Organization:
   {org_info.get('organization_name', 'APPS Nonprofit Corporation')}

2. c/o Name (if applicable):
   {org_info.get('care_of_name', '')}

3. Mailing Address:
   Street: {org_info.get('street_address', '')}
   City: {org_info.get('city', '')}
   State: {org_info.get('state', '')}
   ZIP: {org_info.get('zip_code', '')}

4. Employer Identification Number (EIN):
   {org_info.get('ein', 'XX-XXXXXXX')}

5. Month Tax Year Ends:
   {org_info.get('tax_year_end_month', 'December')}

6. Person to Contact:
   Name: {org_info.get('contact_name', 'Thurman Malik Robinson Jr.')}
   Phone: {org_info.get('contact_phone', '')}
   Email: {org_info.get('contact_email', 'terobinsony@gmail.com')}

7. Organization Website (if applicable):
   {org_info.get('website', 'www.appsnonprofit.com')}

8. Organizing Document:
   [X] Articles of Incorporation
   [ ] Articles of Association
   [ ] Trust Indenture
   [ ] Other: ___________

9. Date Incorporated or Formed:
   {org_info.get('formation_date', '2024-01-01')}

10. State/Country of Domicile:
    {org_info.get('domicile_state', 'Georgia')}

═══════════════════════════════════════════════════════════════
PART II - ORGANIZATIONAL STRUCTURE
═══════════════════════════════════════════════════════════════

11. Is the organization a corporation?
    [X] Yes  [ ] No

12. Does the organization have bylaws?
    [X] Yes  [ ] No

13. Number of voting members on the board of directors:
    {org_info.get('board_members', '3')}

14. Are your officers, directors, or trustees related?
    [ ] Yes  [X] No

═══════════════════════════════════════════════════════════════
PART III - REQUIRED PROVISIONS IN ORGANIZING DOCUMENT
═══════════════════════════════════════════════════════════════

15. Does your organizing document contain:

    a) An exempt purpose from Section 501(c)(3)?
       [X] Yes  [ ] No

       Purpose Statement:
       "{org_info.get('purpose', 'To assertively promote philanthropic services, provide educational resources, support community development, and advance charitable causes through technology and innovation.')}"

    b) A dissolution clause providing that assets will be distributed
       for exempt purposes?
       [X] Yes  [ ] No

       Dissolution Clause Reference: Article {org_info.get('dissolution_article', 'VIII')}

═══════════════════════════════════════════════════════════════
PART IV - FOUNDATION CLASSIFICATION
═══════════════════════════════════════════════════════════════

16. The organization is:
    [X] A public charity (Section 170(b)(1)(A)(vi))
    [ ] A private foundation

17. If public charity, the organization is:
    [X] 509(a)(1) - Publicly supported
    [ ] 509(a)(2) - Gross receipts publicly supported
    [ ] 509(a)(3) - Supporting organization

═══════════════════════════════════════════════════════════════
PART V - REINSTATEMENT AFTER AUTOMATIC REVOCATION
═══════════════════════════════════════════════════════════════

18. Is this application for reinstatement after automatic revocation?
    [ ] Yes  [X] No

═══════════════════════════════════════════════════════════════
PART VI - ELIGIBILITY ATTESTATIONS
═══════════════════════════════════════════════════════════════

The organization attests that:

✓ Gross receipts do NOT exceed $50,000 per year (average over 3 years)
✓ Total assets do NOT exceed $250,000
✓ The organization is NOT a successor to a for-profit entity
✓ The organization will NOT engage in substantial lobbying
✓ The organization will NOT participate in political campaigns
✓ The organization's purposes are exclusively for 501(c)(3) purposes
✓ The organization is NOT a private foundation (public charity)
✓ The organization will NOT be operated for private benefit

Financial Summary (Last 3 Years or Projected):

Year 1: ${org_info.get('year1_revenue', '0')}
Year 2: ${org_info.get('year2_revenue', '0')}
Year 3: ${org_info.get('year3_revenue', '0')}
Average: ${org_info.get('avg_revenue', '0')} (Must be ≤ $50,000)

Total Assets: ${org_info.get('total_assets', '0')} (Must be ≤ $250,000)

═══════════════════════════════════════════════════════════════
PART VII - SIGNATURE AND VERIFICATION
═══════════════════════════════════════════════════════════════

Under penalties of perjury, I declare that I am authorized to sign
this application on behalf of the above organization and that I have
examined this application, including the required attachments, and to
the best of my knowledge it is true, correct, and complete.

Signature: _______________________________  Date: {datetime.now().strftime('%m/%d/%Y')}

Name: {org_info.get('signer_name', 'Thurman Malik Robinson Jr.')}

Title: {org_info.get('signer_title', 'President/Executive Director')}

═══════════════════════════════════════════════════════════════
REQUIRED ATTACHMENTS
═══════════════════════════════════════════════════════════════

Submit the following with Form 1023-EZ:

1. ✓ Organizing document (Articles of Incorporation)
   - Must include purpose statement
   - Must include dissolution clause

2. ✓ Bylaws (recommended but not required for 1023-EZ)

3. ✓ User fee payment: $275
   - Pay online via Pay.gov
   - Account: IRS Form 1023-EZ
   - Or mail check with application

═══════════════════════════════════════════════════════════════
SUBMISSION INSTRUCTIONS
═══════════════════════════════════════════════════════════════

ONLINE SUBMISSION (REQUIRED):
1. Go to: www.pay.gov/paygov/forms/formInstance.html?formTypeId=2&formNumber=1023EZ
2. Complete form electronically
3. Upload organizing document (PDF)
4. Pay $275 user fee via credit card or bank account
5. Submit application
6. Receive confirmation email with tracking number

Note: Form 1023-EZ MUST be submitted electronically via Pay.gov

PROCESSING TIME:
- Average: 2-4 weeks for determination letter
- May request additional information if needed

═══════════════════════════════════════════════════════════════
AFTER APPROVAL
═══════════════════════════════════════════════════════════════

Once approved, you will receive:
✓ IRS Determination Letter confirming 501(c)(3) status
✓ Tax-exempt status effective from date of incorporation
✓ Ability to accept tax-deductible donations
✓ Exemption from federal income tax
✓ Potential state tax exemptions

Annual Filing Requirements:
- File Form 990-N (e-Postcard) if gross receipts < $50,000
- File Form 990-EZ if gross receipts $50,000 - $200,000
- File Form 990 if gross receipts > $200,000

═══════════════════════════════════════════════════════════════

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
By: Agent 5.0 Nonprofit Automation System
"""
        return content

    def generate_articles_of_incorporation(self, org_info: Dict[str, Any]) -> str:
        """Generate Articles of Incorporation with required 501(c)(3) provisions"""

        content = f"""
╔══════════════════════════════════════════════════════════════╗
║            ARTICLES OF INCORPORATION                         ║
║            (501(c)(3) Nonprofit Corporation)                 ║
╚══════════════════════════════════════════════════════════════╝

ARTICLES OF INCORPORATION
OF
{org_info.get('organization_name', 'APPS NONPROFIT CORPORATION').upper()}

The undersigned natural person(s), acting as incorporator(s) of a
corporation under the Nonprofit Corporation Law of {org_info.get('domicile_state', 'Georgia')},
adopt(s) the following Articles of Incorporation:

═══════════════════════════════════════════════════════════════
ARTICLE I - NAME
═══════════════════════════════════════════════════════════════

The name of this corporation is:

    {org_info.get('organization_name', 'APPS Nonprofit Corporation')}

═══════════════════════════════════════════════════════════════
ARTICLE II - DURATION
═══════════════════════════════════════════════════════════════

This corporation shall have perpetual existence.

═══════════════════════════════════════════════════════════════
ARTICLE III - PURPOSE (REQUIRED FOR 501(c)(3))
═══════════════════════════════════════════════════════════════

This corporation is organized exclusively for charitable, educational,
and scientific purposes within the meaning of Section 501(c)(3) of the
Internal Revenue Code of 1986, as amended (the "Code"), including:

1. To assertively promote philanthropic services and charitable giving;

2. To provide educational resources, programs, and opportunities to
   underserved communities;

3. To support community development through technology and innovation;

4. To advance charitable causes including but not limited to poverty
   relief, education, healthcare access, and social justice;

5. To conduct research and provide educational materials related to
   nonprofit management, fundraising, and community service;

6. To make distributions to organizations that qualify as exempt
   organizations under Section 501(c)(3) of the Code;

7. To engage in any lawful activities for which nonprofit corporations
   may be organized under the laws of {org_info.get('domicile_state', 'Georgia')}, provided
   such activities further the exempt purposes stated above.

═══════════════════════════════════════════════════════════════
ARTICLE IV - POWERS
═══════════════════════════════════════════════════════════════

This corporation shall have all powers granted to nonprofit corporations
under the laws of {org_info.get('domicile_state', 'Georgia')}, subject to the limitations
set forth in these Articles and in furtherance of its exempt purposes.

═══════════════════════════════════════════════════════════════
ARTICLE V - LIMITATION ON ACTIVITIES (REQUIRED FOR 501(c)(3))
═══════════════════════════════════════════════════════════════

A. No part of the net earnings of this corporation shall inure to the
   benefit of, or be distributable to, its members, directors, officers,
   or other private persons, except that the corporation shall be
   authorized and empowered to pay reasonable compensation for services
   rendered and to make payments and distributions in furtherance of
   the purposes set forth in Article III.

B. No substantial part of the activities of this corporation shall be
   the carrying on of propaganda, or otherwise attempting to influence
   legislation, and the corporation shall not participate in, or intervene
   in (including the publishing or distribution of statements) any
   political campaign on behalf of or in opposition to any candidate
   for public office.

C. Notwithstanding any other provision of these Articles, this corporation
   shall not carry on any other activities not permitted to be carried on:
   (a) by a corporation exempt from federal income tax under Section
   501(c)(3) of the Code, or (b) by a corporation, contributions to which
   are deductible under Section 170(c)(2) of the Code.

═══════════════════════════════════════════════════════════════
ARTICLE VI - ASSETS AND INCOME
═══════════════════════════════════════════════════════════════

The property, assets, and net income of this corporation are irrevocably
dedicated to charitable, educational, and scientific purposes within the
meaning of Section 501(c)(3) of the Code. No part of the net income or
assets of this corporation shall ever inure to the benefit of any director,
officer, or member, or to the benefit of any private person.

═══════════════════════════════════════════════════════════════
ARTICLE VII - PRIVATE FOUNDATION PROVISIONS
═══════════════════════════════════════════════════════════════

In any taxable year in which this corporation is a private foundation as
described in Section 509(a) of the Code, the corporation:

A. Shall distribute its income for said period at such time and manner
   as not to subject it to tax under Section 4942 of the Code;

B. Shall not engage in any act of self-dealing as defined in Section
   4941(d) of the Code;

C. Shall not retain any excess business holdings as defined in Section
   4943(c) of the Code;

D. Shall not make any investments in such manner as to subject it to
   tax under Section 4944 of the Code; and

E. Shall not make any taxable expenditures as defined in Section
   4945(d) of the Code.

═══════════════════════════════════════════════════════════════
ARTICLE VIII - DISSOLUTION (REQUIRED FOR 501(c)(3))
═══════════════════════════════════════════════════════════════

Upon the dissolution of this corporation, the Board of Directors shall,
after paying or making provision for the payment of all liabilities of
the corporation, dispose of all of the assets of the corporation
exclusively for the purposes of the corporation in such manner, or to
such organization or organizations organized and operated exclusively
for charitable, educational, or scientific purposes as shall at the time
qualify as an exempt organization or organizations under Section 501(c)(3)
of the Code, as the Board of Directors shall determine.

Any such assets not so disposed of shall be disposed of by a court of
competent jurisdiction of the county in which the principal office of the
corporation is then located, exclusively for such purposes or to such
organization or organizations, as said court shall determine, which are
organized and operated exclusively for such purposes.

═══════════════════════════════════════════════════════════════
ARTICLE IX - REGISTERED AGENT AND OFFICE
═══════════════════════════════════════════════════════════════

The name and address of the initial registered agent and registered
office of this corporation are:

Registered Agent: {org_info.get('registered_agent_name', 'Thurman Malik Robinson Jr.')}

Registered Office:
{org_info.get('registered_address_street', '')}
{org_info.get('registered_address_city', '')}, {org_info.get('registered_address_state', 'GA')} {org_info.get('registered_address_zip', '')}

═══════════════════════════════════════════════════════════════
ARTICLE X - INITIAL BOARD OF DIRECTORS
═══════════════════════════════════════════════════════════════

The number of initial directors is {org_info.get('board_members', '3')}, and the names
and addresses of the persons who are to serve as the initial directors are:

{org_info.get('director1_name', 'Director 1 Name')}
{org_info.get('director1_address', 'Address')}

{org_info.get('director2_name', 'Director 2 Name')}
{org_info.get('director2_address', 'Address')}

{org_info.get('director3_name', 'Director 3 Name')}
{org_info.get('director3_address', 'Address')}

═══════════════════════════════════════════════════════════════
ARTICLE XI - INCORPORATOR
═══════════════════════════════════════════════════════════════

The name and address of the incorporator is:

Name: {org_info.get('incorporator_name', 'Thurman Malik Robinson Jr.')}

Address:
{org_info.get('incorporator_address_street', '')}
{org_info.get('incorporator_address_city', '')}, {org_info.get('incorporator_address_state', 'GA')} {org_info.get('incorporator_address_zip', '')}

═══════════════════════════════════════════════════════════════
ARTICLE XII - AMENDMENTS
═══════════════════════════════════════════════════════════════

These Articles of Incorporation may be amended in any manner permitted
by the laws of {org_info.get('domicile_state', 'Georgia')}, provided that no amendment shall
be made which would cause this corporation to cease to qualify as a
corporation described in Section 501(c)(3) of the Code.

═══════════════════════════════════════════════════════════════
INCORPORATOR'S SIGNATURE
═══════════════════════════════════════════════════════════════

IN WITNESS WHEREOF, the undersigned incorporator has executed these
Articles of Incorporation this {datetime.now().strftime('%d day of %B, %Y')}.


_______________________________
{org_info.get('incorporator_name', 'Thurman Malik Robinson Jr.')}
Incorporator

═══════════════════════════════════════════════════════════════

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
By: Agent 5.0 Nonprofit Automation System
"""
        return content

    def save_form_1023_ez(self, org_info: Dict[str, Any]) -> str:
        """Save Form 1023-EZ to file"""
        content = self.generate_form_1023_ez(org_info)
        filename = f"Form_1023-EZ_{org_info.get('organization_name', 'Nonprofit').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(content)

        return filepath

    def save_articles_of_incorporation(self, org_info: Dict[str, Any]) -> str:
        """Save Articles of Incorporation to file"""
        content = self.generate_articles_of_incorporation(org_info)
        filename = f"Articles_of_Incorporation_{org_info.get('organization_name', 'Nonprofit').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(content)

        return filepath


if __name__ == "__main__":
    # Example: Generate for APPS Nonprofit Corporation
    generator = Form1023Generator()

    apps_info = {
        "organization_name": "APPS Nonprofit Corporation",
        "ein": "XX-XXXXXXX",  # Apply for EIN first at irs.gov/ein
        "street_address": "",
        "city": "",
        "state": "GA",
        "zip_code": "",
        "tax_year_end_month": "December",
        "contact_name": "Thurman Malik Robinson Jr.",
        "contact_phone": "",
        "contact_email": "terobinsony@gmail.com",
        "website": "www.appsnonprofit.com",
        "formation_date": "2024-01-01",
        "domicile_state": "Georgia",
        "board_members": "3",
        "purpose": "To assertively promote philanthropic services, provide educational resources, support community development, and advance charitable causes through technology and innovation.",
        "dissolution_article": "VIII",
        "year1_revenue": "0",
        "year2_revenue": "0",
        "year3_revenue": "15000",
        "avg_revenue": "5000",
        "total_assets": "10000",
        "signer_name": "Thurman Malik Robinson Jr.",
        "signer_title": "President",
        "registered_agent_name": "Thurman Malik Robinson Jr.",
        "registered_address_street": "",
        "registered_address_city": "",
        "registered_address_state": "GA",
        "registered_address_zip": "",
        "director1_name": "Thurman Malik Robinson Jr.",
        "director1_address": "",
        "director2_name": "Director 2",
        "director2_address": "",
        "director3_name": "Director 3",
        "director3_address": "",
        "incorporator_name": "Thurman Malik Robinson Jr.",
        "incorporator_address_street": "",
        "incorporator_address_city": "",
        "incorporator_address_state": "GA",
        "incorporator_address_zip": ""
    }

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     501(c)(3) APPLICATION AUTOMATION SYSTEM                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Generate documents
    form_path = generator.save_form_1023_ez(apps_info)
    articles_path = generator.save_articles_of_incorporation(apps_info)

    print(f"✓ Form 1023-EZ generated: {form_path}")
    print(f"✓ Articles of Incorporation generated: {articles_path}")
    print()
    print("═══════════════════════════════════════════════════════════════")
    print("NEXT STEPS:")
    print("═══════════════════════════════════════════════════════════════")
    print()
    print("1. Apply for EIN (Employer Identification Number)")
    print("   URL: https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online")
    print("   Time: 5-10 minutes, receive EIN immediately")
    print()
    print("2. File Articles of Incorporation with Georgia Secretary of State")
    print("   URL: https://ecorp.sos.ga.gov")
    print("   Fee: $100 (Georgia)")
    print("   Time: 2-5 business days")
    print()
    print("3. Submit Form 1023-EZ via Pay.gov")
    print("   URL: https://www.pay.gov/paygov/forms/formInstance.html?formTypeId=2&formNumber=1023EZ")
    print("   Fee: $275")
    print("   Time: 2-4 weeks for IRS determination")
    print()
    print("TOTAL COST: $375 (one-time)")
    print("TOTAL TIME: 6-8 weeks from start to 501(c)(3) approval")
    print()
