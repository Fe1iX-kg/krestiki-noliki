console.log('create_room.js loaded');

// Проверяем, существует ли кнопка
const createRoomBtn = document.getElementById('create-room-btn');
if (!createRoomBtn) {
    console.error('Button with id "create-room-btn" not found');
} else {
    console.log('Button found:', createRoomBtn);

    createRoomBtn.addEventListener('click', async (e) => {
        e.preventDefault(); // Предотвращаем стандартное поведение (например, отправку формы)
        console.log('Create room button clicked');
        try {
            const response = await fetch('/api/rooms/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include',
                body: JSON.stringify({})
            });
            console.log('Create room response status:', response.status);
            if (!response.ok) {
                const text = await response.text();
                console.log('Create room response text:', text);
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Create room data:', data);
            const roomCode = data.code;
            document.getElementById('room-code').style.display = 'block';
            document.getElementById('code').textContent = roomCode;
            alert(`Room created! Code: ${roomCode}`);
        } catch (error) {
            console.error('Error creating room:', error);
            alert('Failed to create room: ' + error.message);
        }
    });
}

function getCookie(name) {
    console.log('Getting cookie:', name);
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    console.log('CSRF token:', cookieValue);
    return cookieValue;
}