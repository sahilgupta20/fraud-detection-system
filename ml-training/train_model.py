FRAUD TAXONOMY - WHAT I'M DETECTING

1. ACCOUNT TAKEOVER (35% of fraud cases)
Pattern:
- Multiple failed login attempts
- Login from new device/location
- Immediately followed by large transaction
- Recipient change + amount change
Detection signals:
→ Failed auth attempts: >3 in 1 hour
→ New device fingerprint
→ Geolocation change >100 miles
→ Transaction within 10 min of login

2. STRUCTURING/SMURFING (25% of cases)
Pattern:
- Multiple transactions just below $10K threshold
- Same recipient, split amounts
- Rapid succession (avoiding CTR reporting)
Example: 
→ $9,800, $9,750, $9,900 in same day
Detection signals:
→ Sum of transactions >$10K in 24hrs
→ Same recipient multiple times
→ Amounts clustered near threshold

3. BUSINESS EMAIL COMPROMISE (20% of cases)
Pattern:
- Email account compromised
- Attacker changes payment instructions
- One-time large wire to new account
Detection signals:
→ Wire to new international recipient
→ Amount >10x average transaction
→ First wire after years of ACH only

4. SYNTHETIC IDENTITY (15% of cases)
Pattern:
- Fake identity using real SSN
- Small transactions to build trust
- Sudden large transaction and disappear
Detection signals:
→ New account (<90 days)
→ Low transaction history
→ Sudden large transaction spike

5. CARD-NOT-PRESENT FRAUD (5% of cases)
Pattern:
- Stolen card details
- Online/phone purchases
- Multiple attempts if declined
Detection signals:
→ Multiple cards tried
→ Shipping address mismatch
→ High-value items (electronics, gift cards)

My System Focuses On: #1, #2, #3 (covers 80% of fraud)

Sources: FBI IC3 Report 2024, ACFE Fraud Study, 
Financial Crimes Enforcement Network (FinCEN)