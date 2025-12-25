#!/bin/bash
# Download State Nonprofit Forms via Surf CLI
# Delegated to: Legal Division - Nonprofit Forms Team

echo "📥 Downloading State Nonprofit Forms..."


echo "📍 Texas Nonprofit Forms..."
npx @surf/cli browse "https://www.sos.state.tx.us/corp/forms_nonprofit.shtml" --task "Download all PDF forms to data/legal_documents/nonprofit_forms/Texas"


echo "📍 Federal Nonprofit Forms..."
npx @surf/cli browse "https://www.irs.gov/charities-non-profits/charitable-organizations/exempt-purposes" --task "Download all PDF forms to data/legal_documents/nonprofit_forms/Federal"

