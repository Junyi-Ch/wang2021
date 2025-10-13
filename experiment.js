/* ---------- Initialize jsPsych ---------- */
const jsPsych = initJsPsych({
  on_finish: () => jsPsych.data.displayData()
});

/* ---------- Word list (Chinese + English) ---------- */
const bilingual_words = [
  { zh: "蚂蚁", en: "ant" }, { zh: "脚踝", en: "ankle" }, { zh: "空调", en: "air conditioner" },
  { zh: "愤怒", en: "anger" }, { zh: "协议", en: "agreement" },
  { zh: "猫", en: "cat" }, { zh: "胳膊", en: "arm" }, { zh: "斧头", en: "ax" },
  { zh: "反感", en: "antipathy" }, { zh: "买卖", en: "business" },
  { zh: "大象", en: "elephant" }, { zh: "耳朵", en: "ear" }, { zh: "床", en: "bed" },
  { zh: "冷漠", en: "apathy" }, { zh: "性质", en: "characteristic" },
  { zh: "长颈鹿", en: "giraffe" }, { zh: "眼睛", en: "eye" }, { zh: "扫帚", en: "broom" },
  { zh: "慈善", en: "charity" }, { zh: "概念", en: "concept" },
  { zh: "熊猫", en: "panda" }, { zh: "手指", en: "finger" }, { zh: "柜子", en: "cabinet" },
  { zh: "舒心", en: "comfortable" }, { zh: "内容", en: "content" },
  { zh: "兔子", en: "rabbit" }, { zh: "膝盖", en: "knee" }, { zh: "椅子", en: "chair" },
  { zh: "死亡", en: "death" }, { zh: "数据", en: "data" },
  { zh: "老鼠", en: "rat" }, { zh: "嘴唇", en: "lips" }, { zh: "筷子", en: "chopsticks" },
  { zh: "债务", en: "debt" }, { zh: "纪律", en: "discipline" },
  { zh: "麻雀", en: "sparrow" }, { zh: "鼻子", en: "nose" }, { zh: "鼠标", en: "computer mouse" },
  { zh: "沮丧", en: "depressed" }, { zh: "作用", en: "effect" },
  { zh: "老虎", en: "tiger" }, { zh: "肩膀", en: "shoulder" }, { zh: "锤子", en: "hammer" },
  { zh: "疾病", en: "disease" }, { zh: "身份", en: "identity" },
  { zh: "乌龟", en: "tortoise" }, { zh: "大腿", en: "thigh" }, { zh: "钥匙", en: "key" },
  { zh: "纠纷", en: "dispute" }, { zh: "方法", en: "method" },
  { zh: "微波炉", en: "microwave" }, { zh: "错误", en: "error" }, { zh: "义务", en: "obligation" },
  { zh: "铅笔", en: "pencil" }, { zh: "兴奋", en: "excited" }, { zh: "现象", en: "phenomenon" },
  { zh: "冰箱", en: "refrigerator" }, { zh: "缘分", en: "fate" }, { zh: "过程", en: "process" },
  { zh: "剪刀", en: "scissors" }, { zh: "过失", en: "fault" }, { zh: "原因", en: "reason" },
  { zh: "沙发", en: "sofa" }, { zh: "恐惧", en: "fear" }, { zh: "关系", en: "relationship" },
  { zh: "勺子", en: "spoon" }, { zh: "骗局", en: "fraud" }, { zh: "结果", en: "result" },
  { zh: "桌子", en: "table" }, { zh: "友情", en: "friendship" }, { zh: "社会", en: "society" },
  { zh: "电视", en: "television" }, { zh: "快乐", en: "happy" }, { zh: "地位", en: "status" },
  { zh: "牙刷", en: "toothbrush" }, { zh: "天堂", en: "heaven" }, { zh: "制度", en: "system" },
  { zh: "洗衣机", en: "washing machine" }, { zh: "敌意", en: "hostility" }, { zh: "团队", en: "team" },
  { zh: "爱心", en: "loving heart" }, { zh: "魔力", en: "magic power" },
  { zh: "婚姻", en: "marriage" }, { zh: "奇迹", en: "miracle" }, { zh: "骄傲", en: "proud" },
  { zh: "难过", en: "sad" }, { zh: "风景", en: "scenery" }, { zh: "光彩", en: "splendor" },
  { zh: "创伤", en: "trauma" }, { zh: "暴力", en: "violence" }
];

/* ---------- Helper functions ---------- */
function getWordsByLanguage(lang) {
  return bilingual_words.map(w => w[lang]);
}

function generateWordCircleHTML(words) {
  const radius = 250;
  const centerX = 300;
  const centerY = 300;
  let html = '<div id="word-container" style="position: relative; width: 600px; height: 600px; margin: auto;">';
  html += '<div id="drop-zone" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:300px;height:300px;border:2px dashed gray;border-radius:50%;"></div>';

  words.forEach((word, i) => {
    const angle = (2 * Math.PI * i) / words.length;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);

    html += `
      <div class="word" draggable="true"
           style="position: absolute; left: ${x}px; top: ${y}px;
                  transform: translate(-50%, -50%);
                  cursor: grab; user-select:none;">
        ${word}
      </div>
    `;
  });

  html += "</div>";
  return html;
}

/* ---------- Trial: Choose Language ---------- */
const lang_choice = {
  type: jsPsychHtmlButtonResponse,
  stimulus: "<p style='font-size:20px;'>Choose your language:</p>",
  choices: ["中文", "English"],
  on_finish: data => {
    const lang = data.response === 0 ? "zh" : "en";
    jsPsych.data.addProperties({ language: lang });
  }
};

/* ---------- Trial: Main word-arrangement task ---------- */
const circleTrial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: () => {
    const lang = jsPsych.data.get().last(1).values()[0].language;
    const words = getWordsByLanguage(lang);
    return generateWordCircleHTML(words);
  },
  choices: "NO_KEYS",
  on_load: () => {
    const words = document.querySelectorAll(".word");

    words.forEach(w => {
      w.addEventListener("click", () => {
        w.classList.toggle("selected");
        w.style.backgroundColor = w.classList.contains("selected") ? "#add8e6" : "";
        w.style.borderRadius = "5px";
        w.style.transition = "0.2s";
      });

      w.addEventListener("dragstart", e => {
        e.dataTransfer.setData("text/plain", w.textContent);
        w.classList.add("dragging");
      });
      w.addEventListener("dragend", e => {
        w.classList.remove("dragging");
      });
    });

    const dropZone = document.getElementById("drop-zone");
    dropZone.addEventListener("dragover", e => e.preventDefault());
    dropZone.addEventListener("drop", e => {
      e.preventDefault();
      const dragging = document.querySelector(".dragging");
      if (dragging) {
        const rect = dropZone.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        dragging.style.left = `${rect.left + x - 15}px`;
        dragging.style.top = `${rect.top + y - 10}px`;
      }
    });
  },
  on_finish: () => {
    const placements = [];
    document.querySelectorAll(".word").forEach(w => {
      const rect = w.getBoundingClientRect();
      placements.push({
        word: w.textContent,
        x: rect.left,
        y: rect.top,
        selected: w.classList.contains("selected")
      });
    });
    jsPsych.data.addData({ placements });
  }
};

/* ---------- Run experiment ---------- */
jsPsych.run([lang_choice, circleTrial]);
