📊 Live Dashboard
👉 Tableau Public: View Interactive Dashboard (coming soon)

🎯 Business Problem

Diversified ETF portfolios are widely assumed to provide broad market diversification.

However, overlapping holdings across ETFs may create hidden concentration risk, where portfolios appear diversified by asset count but remain heavily exposed to the same underlying securities.

This project analyzes ETF holdings data to answer:

Do diversified ETF portfolios truly provide diversification, or does holdings overlap create unintended concentration exposure?

🛠 Tools & Technologies

• Python — Data ingestion, transformation, analytical modeling
• Pandas / NumPy — Portfolio analytics & metric computation
• SQL — Analytical structuring & reproducible metrics layer
• Tableau Public — Interactive dashboard & visual analytics

🔍 Key Insights

✅ Substantial Holdings Overlap Exists Across Major ETFs
Pairwise overlap analysis revealed significant duplication between broad-market ETFs, particularly SPY and VOO.

✅ Weighted Overlap Exposure Reveals Diversification Illusion
Although ETFs hold hundreds of securities, large portions of portfolio weight are concentrated in the same mega-cap stocks.

✅ Diversification by Count ≠ Diversification by Exposure
Portfolios constructed from multiple ETFs contained hundreds of securities but exhibited far fewer effective holdings.

✅ Mega-Cap Dominance Drives Concentration Risk
High-weight securities such as NVIDIA, Apple, and Microsoft consistently dominated portfolio exposure across ETFs.

📈 Analytical Focus

This analysis quantifies:

• Holdings overlap (count-based & weighted)
• Weighted overlap exposure
• Portfolio concentration metrics (HHI)
• Effective number of holdings
• Top holdings exposure concentration

📦 Dataset

ETF Holdings Data

Sources:

• SPY Holdings
• VOO (S&P 500) Holdings
• QQQ Holdings
• SCHD Holdings

🚀 Project Objective

Demonstrate applied portfolio analytics, diversification measurement, and concentration risk diagnostics using Python + SQL + Tableau.

This project simulates real-world investment analytics commonly performed in:

• Portfolio management
• Risk analysis
• Asset allocation strategy
• Investment research
• Financial data analytics
