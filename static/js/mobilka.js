(function () {
    const mainPage = document.getElementById('main_page');
    const chatUser = document.getElementById('chat_user');
    const backBtn = document.getElementById('mobileBackBtn');
    const chatsContainer = document.getElementById('chats_container');

    function isMobile() {
        return window.matchMedia("(max-width: 720px)").matches;
    }

    let mobileChatActive = false;

    function closeMobileChat() {
        if (!isMobile()) return;
        mainPage.style.display = 'block';
        chatUser.style.display = 'none';
        backBtn.style.display = 'none';
        mobileChatActive = false;
        const chatNone = document.getElementById('chat_none');
        if (chatNone) chatNone.style.display = 'none';
    }

    function openMobileChat() {
        if (!isMobile()) return;
        mainPage.style.display = 'none';
        chatUser.style.display = 'block';
        backBtn.style.display = 'flex';
        mobileChatActive = true;
        const chatNone = document.getElementById('chat_none');
        if (chatNone) chatNone.style.display = 'none';
    }

    if (backBtn) {
        backBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            closeMobileChat();
        });
    }

    function onChatClick(chatId) {
        if (typeof window.create_chat === 'function') {
            window.create_chat(chatId);
        } else {
            console.warn('create_chat не определена, но чат будет открыт.');
        }
        if (isMobile()) {
            openMobileChat();
        }
    }

    if (chatsContainer) {
        chatsContainer.addEventListener('click', function (e) {
            const chatButton = e.target.closest('.chat');
            if (!chatButton) return;
            let chatId = chatButton.getAttribute('data-chat-id');
            if (chatId === null) {
                const btnId = chatButton.id;
                if (btnId && btnId.startsWith('chat_')) {
                    chatId = btnId.substring(5);
                }
            }
            if (chatId !== null && chatId !== '') {
                e.preventDefault();
                onChatClick(parseInt(chatId));
            } else {
                console.warn('Не удалось определить ID чата');
            }
        });
    }

    function initMobileLayout() {
        if (isMobile()) {
            mainPage.style.display = 'block';
            chatUser.style.display = 'none';
            backBtn.style.display = 'none';
            mobileChatActive = false;
            const chatNone = document.getElementById('chat_none');
            if (chatNone) chatNone.style.display = 'none';
        } else {
            mainPage.style.display = 'block';
            chatUser.style.display = 'block';
            backBtn.style.display = 'none';
            mainPage.style.position = 'fixed';
            chatUser.style.position = 'absolute';
            mobileChatActive = false;
        }
    }

    window.addEventListener('resize', function () {
        if (!isMobile() && mobileChatActive) {
            mainPage.style.display = 'block';
            chatUser.style.display = 'block';
            backBtn.style.display = 'none';
            mobileChatActive = false;
            mainPage.style.position = 'fixed';
            chatUser.style.position = 'absolute';
        }
        else if (isMobile() && !mobileChatActive) {
            mainPage.style.display = 'block';
            chatUser.style.display = 'none';
            backBtn.style.display = 'none';
        }
        else if (isMobile() && mobileChatActive) {
            mainPage.style.display = 'none';
            chatUser.style.display = 'block';
            backBtn.style.display = 'flex';
        }
        if (!isMobile()) {
            mainPage.style.position = 'fixed';
            chatUser.style.position = 'absolute';
            chatUser.style.display = 'block';
        }
    });

    initMobileLayout();

    if (typeof window.create_chat === 'function') {
        const originalCreateChat = window.create_chat;
        window.create_chat = function (chatId) {
            originalCreateChat(chatId);
            if (isMobile()) {
                openMobileChat();
            }
        };
    }

    const findBtn = document.querySelector('.find_user_btn');
    if (findBtn && typeof window.find_user === 'function') {
        const originalFindUser = window.find_user;
        window.find_user = function () {
            const result = originalFindUser();
            setTimeout(() => {
                if (isMobile() && chatUser && chatUser.style.display !== 'none') {
                    openMobileChat();
                }
            }, 100);
            return result;
        };
    }

    if (isMobile()) {
        const anyChatActive = (chatUser.style.display === 'block' && window.getComputedStyle(chatUser).display === 'block');
        if (!anyChatActive) {
            chatUser.style.display = 'none';
            mainPage.style.display = 'block';
        } else {
            backBtn.style.display = 'flex';
            mainPage.style.display = 'none';
            mobileChatActive = true;
        }
    }
})();


