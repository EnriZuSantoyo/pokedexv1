
// Código Javascript para el pokedex


// Llenamos el dropdown al cargar la página tras validar el token 
document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return;
  }

  try {
    await axios.get("http://localhost:8000/datos", {
      headers: { Authorization: `Bearer ${token}` },
    });
    llenarDropdown();
  } catch (err) {
    console.error("Token inválido:", err);
    window.location.href = "index.html";
  }
});

async function llenarDropdown() {
  const dropdown = document.getElementById("pokeDropdown");
  try {
    const res = await axios.get("http://localhost:8000/dropdown");
    dropdown.innerHTML = `<option value="">Selecciona un Pokémon</option>`;
    res.data.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.name;
      opt.text = `#${p.pokeId} - ${p.name}`;
      dropdown.appendChild(opt);
    });
  } catch (err) {
    console.error("Error llenando dropdown:", err);
  }
}

document.getElementById("botonRandom").onclick = function () {
  const id = Math.floor(Math.random() * 1025) + 1;
  buscaPokemon(id.toString());
};

document.getElementById("botonBuscar").onclick = function () {
  const nombre = document.getElementById("fieldBusqueda").value.trim().toLowerCase();
  buscaPokemon(nombre);
};

function buscaDropdown() {
  const nombre = document.getElementById("pokeDropdown").value.trim().toLowerCase();
  if (nombre) buscaPokemon(nombre);
}

function buscaPokemon(nombre) {
  if (!nombre) return alert("Ingresa un nombre o ID");

  let url = /^\d+$/.test(nombre)
    ? `http://localhost:8000/pokemon/${nombre}`
    : `http://localhost:8000/pokemon/name/${nombre}`;

  axios
    .get(url)
    .then((res) => {
      const data = res.data;
      document.getElementById("nombrePoke").innerHTML = `#${data.pokeId} ${data.name}`;
      document.querySelector(".pokeSprite2").src = data.sprite;
      document.getElementById("pokeDescription").innerHTML = data.description;
      document.getElementById("pokeType1").innerHTML = data.type1;
      document.getElementById("pokeType2").innerHTML = data.type2 || "N/A";
      document.getElementById("pokeAltura").innerHTML = data.altura;
      document.getElementById("pokePeso").innerHTML = data.peso;
      document.getElementById("pokeGeneracion").innerHTML = data.generation;
      document.getElementById("pokeLegendario").innerHTML = data.legendario;
    })
    .catch((err) => {
      console.error(err);
      alert("¡Pokémon no encontrado!");
    });
}