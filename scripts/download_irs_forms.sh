
# Surf CLI Automation - Download IRS Forms
# Delegated to: Web Automation Team (10 Surf agents)


echo "📥 Downloading Form 1023-EZ..."
curl -L "https://www.irs.gov/pub/irs-pdf/f1023ez.pdf" -o "data/legal_documents/irs_forms/Form_1023-EZ.pdf" || \
  npx @surf/cli browse "https://www.irs.gov/pub/irs-pdf/f1023ez.pdf" --download "data/legal_documents/irs_forms/Form_1023-EZ.pdf"

echo "📥 Downloading Form 1023..."
curl -L "https://www.irs.gov/pub/irs-pdf/f1023.pdf" -o "data/legal_documents/irs_forms/Form_1023.pdf" || \
  npx @surf/cli browse "https://www.irs.gov/pub/irs-pdf/f1023.pdf" --download "data/legal_documents/irs_forms/Form_1023.pdf"

echo "📥 Downloading Form 990..."
curl -L "https://www.irs.gov/pub/irs-pdf/f990.pdf" -o "data/legal_documents/irs_forms/Form_990.pdf" || \
  npx @surf/cli browse "https://www.irs.gov/pub/irs-pdf/f990.pdf" --download "data/legal_documents/irs_forms/Form_990.pdf"

echo "📥 Downloading Form 990-EZ..."
curl -L "https://www.irs.gov/pub/irs-pdf/f990ez.pdf" -o "data/legal_documents/irs_forms/Form_990-EZ.pdf" || \
  npx @surf/cli browse "https://www.irs.gov/pub/irs-pdf/f990ez.pdf" --download "data/legal_documents/irs_forms/Form_990-EZ.pdf"

echo "📥 Downloading Form W-9..."
curl -L "https://www.irs.gov/pub/irs-pdf/fw9.pdf" -o "data/legal_documents/irs_forms/Form_W-9.pdf" || \
  npx @surf/cli browse "https://www.irs.gov/pub/irs-pdf/fw9.pdf" --download "data/legal_documents/irs_forms/Form_W-9.pdf"

echo "📥 Downloading Form SS-4..."
curl -L "https://www.irs.gov/pub/irs-pdf/fss4.pdf" -o "data/legal_documents/irs_forms/Form_SS-4.pdf" || \
  npx @surf/cli browse "https://www.irs.gov/pub/irs-pdf/fss4.pdf" --download "data/legal_documents/irs_forms/Form_SS-4.pdf"
