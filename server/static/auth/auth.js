document.getElementById('authForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/user/auth_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ login, password }),
        });

        if (!response.ok) {
            const errorResult = await response.json();
            displayMessage(errorResult);
            return;
        }

        const result = await response.json();
        displayMessage(result);

        if (result.success) {
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        displayMessage({ success: false, message: 'Произошла ошибка при связи с сервером.' });
    }
});


document.getElementById('registerForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const login = document.getElementById('regLogin').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('regPassword').value;

    const response = await fetch('/user/create_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            login: login,
            password: password,
            mail: email
        })
    });

    const result = await response.json();

    displayMessage(result);
});


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
