/*-------------- SCROLL TO TOP --------------*/
const scrollToTopBtn = document.getElementById('scrollToTopBtn');
window.onscroll = function() { scrollFunction(); };
function scrollFunction() {
  if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
    scrollToTopBtn.style.display = 'block';
  } else {
    scrollToTopBtn.style.display = 'none';
  }
}
scrollToTopBtn.addEventListener('click', function() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
});


/*-------------- ACCORDION --------------*/
const accordionToggles = document.querySelectorAll('.accordion-toggle');
accordionToggles.forEach(toggle => {
  toggle.addEventListener('click', () => {
    toggle.classList.toggle('active');
    const content = toggle.nextElementSibling;
    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + 'px';
    }
  });
});

/*-------------- MODAL --------------*/
function openModal() {
  document.getElementById('moreInfoModal').style.display = 'block';
}
function closeModal() {
  document.getElementById('moreInfoModal').style.display = 'none';
}
window.onclick = function(event) {
  const modal = document.getElementById('moreInfoModal');
  if (event.target === modal) {
    modal.style.display = 'none';
  }
};

/*-------------- CHATBOT LOGIC --------------*/
/*-------------- CHATBOT LOGIC --------------*/
/*-------------- CHATBOT LOGIC --------------*/
function toggleChatWindow() {
  const chatWindow = document.getElementById('chatWindow');
  chatWindow.style.display = (chatWindow.style.display === 'flex') ? 'none' : 'flex';
}

function handleEnter(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
}

function getBotResponse(userMessage) {
  const msg = userMessage.toLowerCase();

  // 1) Greeting / Basic
  if (msg.includes('hello') || msg.includes('hi')) {
    return (
      "Hello! Welcome to the Weather Station chatbot. How can I assist you with our project today?"
    );
  }

  // 2) Project Objective
  if (msg.includes('objective') || msg.includes('purpose') || msg.includes('what do you do')) {
    return (
      "Our project aims to provide an easy-to-use, non-bulky weather station. Unlike traditional stations that focus on forecasting, we prioritize visualizing live weather data in real-time with just a click of a button. It's designed to be accessible in the comfort of your own home."
    );
  }

  // 3) How Does It Work
  if (msg.includes('how does it work') || msg.includes('how does this work') || msg.includes('how is it built')) {
    return (
      "The weather station uses a sensors connected to a Raspberry Pi to collect live weather data. The data is displayed on a user-friendly dashboard, allowing you to see real-time updates on temperature, humidity, and other weather parameters. All of our code is open-source, so you can review, modify, or contribute."
    );
  }

  // 4) Raspberry Pi (Hardware-related questions)
  if (msg.includes('raspberry pi') || msg.includes('hardware') || msg.includes('raspberry pi 4')) {
    return (
      "The Raspberry Pi is used as the core processor for the weather station. It collects data from the sensors, processes it, and displays the results on the web dashboard. It's a small, efficient computer that helps keep the system compact and easy to use."
    );
  }
  // 5)Sensors 
  if (msg.includes('sensors')||msg.includes('how sensor works')) {
    return (
      "For our sensors, we used a Pi Camera to collect cloud data, a DHT22 sensor to measure temperature and humidity, and a raindrop sensor to measure precipitation. Image processing, such as edge detection and Local Binary Pattern, is applied to the images to obtain cloud data, such as edge count, texture of clouds and HSV data of clouds. These sensors are connected to the Raspberry Pi, which processes the data and displays it on the dashboard."
    );
  }

  // 6) Live Data Collection
  if (msg.includes('live data') || msg.includes('real-time data') || msg.includes('collecting data') || msg.includes('weather data')) {
    return (
      "Our system collects live data from the sensors in real-time. Whether it's temperature, humidity, or other weather conditions, with just one click of a button, the system updates instantly on the dashboard, allowing you to view current environmental parameters."
    );
  }

  // 7) Open Source Code
  if (msg.includes('open source') || msg.includes('code') || msg.includes('software')) {
    return (
      "Yes, all of our code is open-source. This means anyone can access, modify, or contribute to the project. This approach ensures transparency and allows for continuous improvement by the community."
    );
  }

  // 8) Personalized Data
  if (msg.includes('personalized') || msg.includes('customize') || msg.includes('personalization')) {
    return (
      "Our system allows for personalized data visualization. You can focus on the weather conditions that are most important to you and track those in real-time, making it easy to monitor your specific needs."
    );
  }

  // 9) Data Privacy
  if (msg.includes('privacy') || msg.includes('secure') || msg.includes('data security')) {
    return (
      "Your data is stored securely, and since our code is open-source, you can see how the system handles data storage and usage. We prioritize transparency and ensure that your user data is protected."
    );
  }

  // 10) FAQs (For miscellaneous questions)
  if (msg.includes('frequently asked questions') || msg.includes('faq') || msg.includes('help') || msg.includes('support')) {
    return (
      "You can ask about the project objectives, the hardware we use, how live data is collected, or how to access our open-source code. If you have other questions, feel free to ask!"
    );
  }

  // 11) Thank-you
  if (msg.includes('thank') || msg.includes('thanks')) {
    return (
      "You're welcome! I'm happy to help. If you have more questions, feel free to ask!"
    );
  }

  // 12) Fallback: Not sure
  return (
    "I'm not sure what you're asking. Here are some topics I can help with:\n" +
    "• Purpose of the weather station project\n" +
    "• How the system works\n" +
    "• Raspberry Pi details\n" +
    "• Live data collection\n" +
    "• Open-source code\n" +
    "• Personalized data collection\n\n" +
    "You can try asking: “How does the system collect live data?” or “What is the project objective?”"
  );
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  const chatBody = document.getElementById('chatBody');
  const userMessage = input.value.trim();

  if (!userMessage) return;

  // Show user message
  chatBody.innerHTML += `<div class="user-msg">${userMessage}</div>`;
  input.value = '';
  chatBody.scrollTop = chatBody.scrollHeight;

  // Generate bot response
  const botReply = getBotResponse(userMessage);
  chatBody.innerHTML += `<div class="bot-msg">${botReply}</div>`;
  chatBody.scrollTop = chatBody.scrollHeight;
}



/*-------------- FILTER CARDS --------------*/
function filterCards() {
  const searchInput = document.getElementById('searchInput');
  const filterValue = searchInput.value.toLowerCase();
  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {
    const sensorType = card.getAttribute('data-sensor');
    if (sensorType.toLowerCase().includes(filterValue) || filterValue === '') {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

