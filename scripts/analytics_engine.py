
import pandas as pd
import os
import glob
from datetime import datetime

def analyze_shorts_performance(analytics_dir):
    """
    Data Engineering: Processes YouTube Analytics exports to find winning patterns.
    """
    print(f"📊 Analyzing analytics in: {analytics_dir}")
    
    # Path to the specific export folder
    target_folders = glob.glob(os.path.join(analytics_dir, "Contenu*"))
    if not target_folders:
        print("❌ No analytics folders found.")
        return
    
    latest_folder = max(target_folders, key=os.path.getctime)
    csv_path = os.path.join(latest_folder, "Informations relatives aux tableaux.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ Could not find video stats CSV at: {csv_path}")
        return

    # Load data
    df = pd.read_csv(csv_path)
    
    # Filter out the "Total" row
    df = df[df['Contenu'] != 'Total']
    
    # Clean views
    df['Vues'] = pd.to_numeric(df['Vues'], errors='coerce').fillna(0)
    df['Durée'] = pd.to_numeric(df['Durée'], errors='coerce').fillna(0)
    
    # Sort by views
    top_vids = df.sort_values(by='Vues', ascending=False).head(10)
    
    print("\n🏆 TOP 5 PERFORMING VIDEOS:")
    for i, row in top_vids.head(5).iterrows():
        print(f"   - {row['Titre de la vidéo']}: {int(row['Vues'])} views ({row['Durée']}s)")

    # Find correlation between duration and views
    avg_duration_top = top_vids['Durée'].mean()
    print(f"\n📈 INSIGHT: Top 10 videos average duration: {avg_duration_top:.1f}s")
    
    # Find keyword frequency in titles
    all_titles = " ".join(df['Titre de la vidéo'].astype(str).tolist()).lower()
    keywords = ["unsolved", "real story", "mystery", "shocking", "true story", "winter"]
    kw_stats = {}
    for kw in keywords:
        kw_stats[kw] = all_titles.count(kw)
    
    print("\n🏷️ KEYWORD PERFORMANCE (Frequency in successful videos):")
    for kw, count in sorted(kw_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {kw}: {count} appearances")

    # Generate Recommendations for Factory Configuration
    recommended_duration = 14 if avg_duration_top < 20 else 25
    
    recommendations = {
        "target_duration": recommended_duration,
        "hooks": ["UNSOLVED", "REAL STORY"] if kw_stats["unsolved"] > kw_stats["mystery"] else ["MYSTERY", "SHOCKING"],
        "visual_style": "high_contrast_cinematic"
    }
    
    print("\n💡 DATA-DRIVEN PROPOSAL:")
    print(f"   1. Target Duration: {recommendations['target_duration']}s (Optimize for completion rate)")
    print(f"   2. Priority Hooks: {recommendations['hooks']}")
    print(f"   3. Visual Update: Move to Dynamic Ken Burns + Kinetic Subtitles")
    
    return recommendations

if __name__ == "__main__":
    analytics_path = "/Users/zacksaccount/Desktop/AI_Shorts_Project/analytics"
    analyze_shorts_performance(analytics_path)
