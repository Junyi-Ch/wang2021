import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# Load ISC file
df_isc = pd.read_csv("results/step1_subject_bootstrap_stats.csv")

# Load word order
df_words = pd.read_csv("preprocessed/word_order.csv", encoding="utf-8-sig")

# Create word_index from row order
df_words = df_words.reset_index().rename(columns={"index": "word_index", "word": "word_zh"})

# Merge
df = df_isc.merge(df_words, on="word_index", how="left")

# ============================================
# Define categories
# ============================================

animals = {
    "蚂蚁","猫","大象","长颈鹿","熊猫","兔子","老鼠","麻雀","老虎","乌龟"
}
bodyparts = {
    "脚踝","胳膊","耳朵","眼睛","手指","膝盖","嘴唇","鼻子","肩膀","大腿"
}
artifacts = {
    "空调","斧头","床","扫帚","柜子","椅子","筷子","鼠标","锤子","钥匙",
    "微波炉","铅笔","冰箱","剪刀","沙发","勺子","桌子","电视","牙刷","洗衣机"
}
emotional = {
    "愤怒","反感","冷漠","慈善","舒心","死亡","债务","沮丧","疾病","纠纷",
    "错误","兴奋","缘分","过失","恐惧","骗局","友情","快乐","天堂","敌意",
    "爱心","魔力","婚姻","奇迹","骄傲","难过","风景","光彩","创伤","暴力"
}
nonemotional = {
    "协议","买卖","性质","概念","内容","数据","纪律","作用","身份","方法",
    "义务","现象","过程","原因","关系","结果","社会","地位","制度","团队"
}

def assign_cat(w):
    if w in animals: return "Animal"
    if w in bodyparts: return "BodyPart"
    if w in artifacts: return "Artifact"
    if w in emotional: return "Emotional"
    if w in nonemotional: return "NonEmotional"
    return "Unknown"

df["category"] = df["word_zh"].apply(assign_cat)

# ============================================
# Create abstract vs concrete groups
# ============================================

concrete = df[df["category"].isin(["Animal","BodyPart","Artifact"])]["mean"]
abstract = df[df["category"].isin(["Emotional","NonEmotional"])]["mean"]

print("Concrete words:", len(concrete))
print("Abstract words:", len(abstract))

# ============================================
# Independent-samples t-test
# ============================================

t, p = ttest_ind(concrete, abstract, equal_var=True)

# ============================================
# Cohen's d
# ============================================

sd1 = concrete.std(ddof=1)
sd2 = abstract.std(ddof=1)
n1, n2 = len(concrete), len(abstract)

spooled = np.sqrt(((n1-1)*sd1**2 + (n2-1)*sd2**2)/(n1+n2-2))
d = (concrete.mean() - abstract.mean()) / spooled

# CI
se = spooled * np.sqrt(1/n1 + 1/n2)
mean_diff = concrete.mean() - abstract.mean()
ci_low = mean_diff - 1.96*se
ci_high = mean_diff + 1.96*se

print("\n===== RESULTS =====")
print(f"Concrete mean: {concrete.mean():.4f} (SD={sd1:.4f})")
print(f"Abstract mean: {abstract.mean():.4f} (SD={sd2:.4f})")
print(f"t({n1+n2-2}) = {t:.4f}, p = {p:.3e}")
print(f"Cohen's d = {d:.4f}")
print(f"95% CI of mean difference: [{ci_low:.4f}, {ci_high:.4f}]")
print("\nDirection:", "Concrete > Abstract" if d>0 else "Abstract > Concrete")
