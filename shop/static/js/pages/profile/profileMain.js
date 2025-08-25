function getProfileMetaConfig() {
  const metaTag = document.querySelector('meta[name="profileConfig"]');
  if (metaTag) {
    try {
      return JSON.parse(metaTag.getAttribute("content"));
    } catch (e) {
      console.error("Error while parsing mini-cart-urls", e);
    }
  } else {
    console.error('Meta tag "django-urls" has not been found');
  }
  return {};
}
const profileConfig = getProfileMetaConfig();

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.active-page').forEach(element => {
        element.classList.remove('active');
    });
    let queryclass= '.page-'+  profileConfig.featureName;
    document.querySelector(queryclass).classList.add('active');

})
function toggleChat() {
    const chatContainer = document.getElementById('chat-container');

    if (chatContainer.classList.contains('hidden')) {
        // Если контейнер скрыт, убираем класс hidden и показываем элемент
        chatContainer.classList.remove('hidden');
        chatContainer.classList.add('show');
        chatContainer.style.display = 'block';
    } else if (chatContainer.classList.contains('show')) {
        // Если контейнер показан, скрываем его
        chatContainer.classList.remove('show');
        chatContainer.classList.add('hidden');

        // Ожидаем завершения анимации и затем скрываем элемент
    } else {
        // В случае если элемент не имеет ни одного из классов, просто показываем его
        chatContainer.classList.add('show');
        chatContainer.style.display = 'block';
    }
}
