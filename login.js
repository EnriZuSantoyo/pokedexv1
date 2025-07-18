
document.getElementById("botonLogin")?.addEventListener("click", async () => {
  const usuario = document.getElementById("fieldUsuario").value;
  const contraseña = document.getElementById("fieldPassword").value;
  await llamarLogin(usuario, contraseña);
});

document.getElementById("botonToken")?.addEventListener("click", async () => {
  const token = document.getElementById("fieldToken").value;
  await validarToken(token);
});

// Validamos las credenciales 
document.getElementById("botonAddUser")?.addEventListener("click", () => {
  const user = document.getElementById("fieldUsuarioNew").value;
  const pass1 = document.getElementById("fieldPasswordNew").value;
  const pass2 = document.getElementById("fieldPasswordNew2").value;

  if (!user || !pass1 || !pass2) {
    document.getElementById("mensajeAddUsuario").innerHTML = "<b>Los campos no pueden estar vacíos</b>";
  } else if (pass1 !== pass2) {
    document.getElementById("mensajeAddUsuario").innerHTML = "<b>Las contraseñas deben ser iguales</b>";
  } else {
    crearUsuario(user, pass1);
  }
});

// Desplegar la zona de agregar usuarios 
document.getElementById("botonDesplegarAddUser")?.addEventListener("click", () => {
  document.getElementById("zonaAddUsuarios").style.display = "block";
  document.getElementById("botonDesplegarAddUser").style.display = "none";
});

//Hacemos login para redirigir hacia el pokedex 
async function llamarLogin(usuario, contraseña) {
  const credenciales = { usuario, password: contraseña };
  try {
    const res = await axios.post("http://127.0.0.1:8000/login", credenciales);
    localStorage.setItem("token", res.data.token);
    window.location.href = "pokedex.html";
  } catch (err) {
    console.error("Login fallido", err);
  }
}

//Validamos qu el token sea correcto y desplegamos su contenido 
async function validarToken(token) {
  try {
    const res = await axios.get("http://127.0.0.1:8000/datos", {
      headers: { Authorization: `Bearer ${token}` },
    });
    document.getElementById("mensaje").innerHTML = res.data.mensaje;
    document.getElementById("notificaciones").innerHTML = `Notificaciones: ${res.data.notificaciones}`;
    document.getElementById("rol").innerHTML = `Rol: ${res.data.rol}`;
    document.getElementById("zonaToken").style.display = "none";
    document.getElementById("zonaAPIs").style.display = "block";
    document.getElementById("botonDesplegarAddUser").style.display = "block";
  } catch (err) {
    console.error("Token inválido", err);
  }
}

// Crear usuarios nuevos 
function crearUsuario(user, pass) {
  const credenciales = { usuario: user, password: pass };
  axios
    .post("http://127.0.0.1:8000/altas", credenciales)
    .then((res) => {
      document.getElementById("mensajeAddUsuario").innerHTML = `<b>${res.data.mensaje}</b>`;
    })
    .catch((err) => {
      document.getElementById("mensajeAddUsuario").innerHTML = `<b>${err.response.data.detail}</b>`;
    });
}
