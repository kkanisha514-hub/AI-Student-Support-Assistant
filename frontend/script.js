const API_BASE = "http://localhost:8000/api";


/* =====================================================
   LOCAL STORAGE
===================================================== */

let sessionId =
  localStorage.getItem("ai_ssa_session_id") || null;

let studentId =
  localStorage.getItem("ai_ssa_student_id") || null;


/* =====================================================
   ELEMENTS
===================================================== */

const chatArea =
  document.getElementById("chatArea");

const chatForm =
  document.getElementById("chatForm");

const chatInput =
  document.getElementById("chatInput");

const errorBanner =
  document.getElementById("errorBanner");

const connStatus =
  document.getElementById("connStatus");

const connectionText =
  document.getElementById("connectionText");

const historyList =
  document.getElementById("historyList");

const sendButton =
  document.getElementById("sendButton");


/* =====================================================
   ADD MESSAGE
===================================================== */

function addMessage(role, content) {

  const wrap = document.createElement("div");

  wrap.className = `message ${role}`;


  /*
   * USER MESSAGE
   */

  if (role === "user") {

    const bubble =
      document.createElement("div");

    bubble.className =
      "bubble user-bubble";

    bubble.textContent = content;

    wrap.appendChild(bubble);
  }


  /*
   * ASSISTANT MESSAGE
   */

  else {

    const avatar =
      document.createElement("div");

    avatar.className =
      "avatar-small";

    avatar.textContent = "AI";


    const bubble =
      document.createElement("div");

    bubble.className =
      "bubble assistant-bubble";

    bubble.textContent = content;


    wrap.appendChild(avatar);

    wrap.appendChild(bubble);
  }


  chatArea.appendChild(wrap);

  chatArea.scrollTop =
    chatArea.scrollHeight;


  return wrap;
}


/* =====================================================
   LOADING
===================================================== */

function addLoadingBubble() {

  const wrap =
    document.createElement("div");

  wrap.className =
    "message assistant";

  wrap.id =
    "loadingBubble";


  const avatar =
    document.createElement("div");

  avatar.className =
    "avatar-small";

  avatar.textContent =
    "AI";


  const bubble =
    document.createElement("div");

  bubble.className =
    "bubble assistant-bubble loading-dots";


  bubble.innerHTML = `
    <span></span>
    <span></span>
    <span></span>
  `;


  wrap.appendChild(avatar);

  wrap.appendChild(bubble);

  chatArea.appendChild(wrap);

  chatArea.scrollTop =
    chatArea.scrollHeight;
}


function removeLoadingBubble() {

  const el =
    document.getElementById("loadingBubble");

  if (el) {
    el.remove();
  }
}


/* =====================================================
   ERROR
===================================================== */

function showError(message) {

  errorBanner.textContent =
    message;

  errorBanner.classList.remove(
    "hidden"
  );


  setTimeout(() => {

    errorBanner.classList.add(
      "hidden"
    );

  }, 5000);
}


/* =====================================================
   CONNECTION STATUS
===================================================== */

function setOnline() {

  connStatus.classList.remove(
    "offline"
  );

  connectionText.textContent =
    "Connected";
}


function setOffline() {

  connStatus.classList.add(
    "offline"
  );

  connectionText.textContent =
    "Offline";
}


/* =====================================================
   SEND MESSAGE
===================================================== */

async function sendMessage(message) {

  addMessage(
    "user",
    message
  );

  addLoadingBubble();

  sendButton.disabled = true;


  try {

    const response =
      await fetch(
        `${API_BASE}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({

            message: message,

            session_id:
              sessionId,

            student_id:
              studentId
                ? parseInt(studentId)
                : null

          })
        }
      );


    if (!response.ok) {

      const error =
        await response
          .json()
          .catch(() => ({}));

      throw new Error(
        error.detail ||
        `Server error (${response.status})`
      );
    }


    const data =
      await response.json();


    /*
     * SAVE SESSION
     */

    sessionId =
      data.session_id;

    localStorage.setItem(
      "ai_ssa_session_id",
      sessionId
    );


    removeLoadingBubble();


    /*
     * IMPORTANT:
     *
     * We only display data.answer.
     *
     * data.sources is intentionally
     * NOT displayed.
     */

    addMessage(
      "assistant",
      data.answer
    );


    setOnline();

    updateHistory();


  } catch (error) {

    removeLoadingBubble();

    showError(
      "⚠️ " + error.message
    );

    setOffline();

  } finally {

    sendButton.disabled = false;

    chatInput.focus();
  }
}


/* =====================================================
   CHAT FORM
===================================================== */

chatForm.addEventListener(
  "submit",
  function (event) {

    event.preventDefault();


    const message =
      chatInput.value.trim();


    if (!message) {
      return;
    }


    chatInput.value = "";


    sendMessage(message);
  }
);


/* =====================================================
   NEW CHAT
===================================================== */

document
  .getElementById("newChatBtn")
  .addEventListener(
    "click",
    function () {

      sessionId = null;

      localStorage.removeItem(
        "ai_ssa_session_id"
      );


      chatArea.innerHTML = "";


      addMessage(
        "assistant",
        "👋 Started a new conversation. How can I help you today?"
      );


      historyList.innerHTML = `
        <li class="empty-history">
          💬 New conversation
        </li>
      `;

      chatInput.focus();
    }
  );


/* =====================================================
   SAVE PROFILE
===================================================== */

document
  .getElementById("saveProfileBtn")
  .addEventListener(
    "click",
    async function () {

      const name =
        document
          .getElementById("studentName")
          .value
          .trim();


      const department =
        document
          .getElementById("studentDept")
          .value;


      const year =
        document
          .getElementById("studentYear")
          .value;


      const status =
        document
          .getElementById("profileStatus");


      status.textContent =
        "Saving...";


      try {

        const response =
          await fetch(
            `${API_BASE}/students`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body: JSON.stringify({

                name:
                  name || null,

                department_code:
                  department || null,

                year:
                  year
                    ? parseInt(year)
                    : null

              })
            }
          );


        if (!response.ok) {

          throw new Error(
            "Failed to save profile"
          );
        }


        const data =
          await response.json();


        studentId =
          data.id;


        localStorage.setItem(
          "ai_ssa_student_id",
          studentId
        );


        status.textContent =
          "✓ Profile saved successfully";


      } catch (error) {

        status.textContent =
          "⚠️ Could not save profile";
      }
    }
  );


/* =====================================================
   LOAD CHAT HISTORY
===================================================== */

async function loadHistory() {

  if (!sessionId) {

    historyList.innerHTML = `
      <li class="empty-history">
        💬 No conversations yet
      </li>
    `;

    return;
  }


  try {

    const response =
      await fetch(
        `${API_BASE}/chat/history/${sessionId}`
      );


    if (!response.ok) {
      return;
    }


    const messages =
      await response.json();


    chatArea.innerHTML = "";


    messages.forEach(
      function (message) {

        /*
         * Sources are ignored.
         */

        addMessage(
          message.role,
          message.content
        );
      }
    );


    updateHistory();


  } catch (error) {

    console.log(
      "History loading failed:",
      error
    );
  }
}


/* =====================================================
   HISTORY UI
===================================================== */

function updateHistory() {

  if (!sessionId) {

    historyList.innerHTML = `
      <li class="empty-history">
        💬 No conversations yet
      </li>
    `;

    return;
  }


  historyList.innerHTML = `
    <li>
      💬 Conversation ${sessionId.slice(0, 8)}
    </li>
  `;
}


/* =====================================================
   HEALTH CHECK
===================================================== */

async function checkHealth() {

  try {

    const response =
      await fetch(
        `${API_BASE}/health`
      );


    if (response.ok) {

      setOnline();

    } else {

      setOffline();
    }


  } catch (error) {

    setOffline();
  }
}


/* =====================================================
   START
===================================================== */

checkHealth();

loadHistory();

chatInput.focus();