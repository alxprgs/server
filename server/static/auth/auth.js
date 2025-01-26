document.getElementById('authForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    const result = await sendAuthRequest({ login, password });
    displayMessage(result);

    if (result.status) {
        setTimeout(() => {
            window.location.href = '/';
        }, 3000);
    }
});

document.getElementById('registerForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const login = document.getElementById('regLogin').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('regPassword').value;

    const result = await sendRegisterRequest({ login, password, mail: email });
    displayMessage(result);
});

async function sendAuthRequest({ login, password }) {
    try {
        const response = await fetch('/user/auth_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ login, password }),
        });

        if (!response.ok) {
            return await response.json();
        }

        return await response.json();
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        return { success: false, message: 'Произошла ошибка при связи с сервером.' };
    }
}

async function sendRegisterRequest({ login, password, mail }) {
    try {
        const response = await fetch('/user/create_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ login, password, mail })
        });

        return await response.json();
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        return { success: false, message: 'Произошла ошибка при связи с сервером.' };
    }
}

document.getElementById('showRegister').addEventListener('click', function () {
    document.querySelector('h1:nth-of-type(1)').style.display = 'none';
    document.getElementById('authForm').style.display = 'none';
    
    document.querySelector('h1:nth-of-type(2)').style.display = 'block';
    document.getElementById('registerForm').style.display = 'block';
});

document.getElementById('showAuth').addEventListener('click', function () {
    document.querySelector('h1:nth-of-type(2)').style.display = 'none';
    document.getElementById('registerForm').style.display = 'none';
    
    document.querySelector('h1:nth-of-type(1)').style.display = 'block';
    document.getElementById('authForm').style.display = 'block';
});

function displayMessage(result) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = result.message;
    messageDiv.style.color = result.status ? 'green' : 'red';
}
