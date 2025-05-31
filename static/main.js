document.addEventListener("DOMContentLoaded", function() {
  // Data mata kuliah per semester
  const matkulData = {
    1: [
      "Pemrograman Dasar",
      "Statistik dan Probabilitas",
      "Matematika Diskrit",
      "Pengantar Teknologi Informasi"
    ],
    2: [
      "Struktur Data",
      "Aljabar Linier",
      "Pemrograman Berorientasi Objek",
      "Logika Matematika"
    ]
  };

  // Fungsi untuk mengisi pilihan mata kuliah sesuai semester
  function updateMatkulOptions() {
    const semester = document.getElementById("semester").value;
    const matkulSelect = document.getElementById("matkul");
    matkulSelect.innerHTML = "";
    if (matkulData[semester]) {
      matkulData[semester].forEach(matkul => {
        const option = document.createElement("option");
        option.value = matkul;
        option.textContent = matkul;
        matkulSelect.appendChild(option);
      });
    }
  }

  // Event: Ganti semester
  const semesterSelect = document.getElementById("semester");
  if (semesterSelect) {
    semesterSelect.addEventListener("change", updateMatkulOptions);
  }

  // Event: Submit form pilihan
  const pilihanForm = document.getElementById("pilihanForm");
  if (pilihanForm) {
    pilihanForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const semester = document.getElementById("semester").value;
      const matkul = document.getElementById("matkul").value;
      const resultInfo = document.getElementById("resultInfo");
      if (resultInfo) {
        resultInfo.style.display = "block";
        resultInfo.textContent = `Semester ${semester} - Mata Kuliah: ${matkul}`;
      }
    });
  }

  // Event: Tombol Mulai Belajar
  const mulaiBtn = document.querySelector(".mulai-btn");
  if (mulaiBtn) {
    mulaiBtn.addEventListener("click", function() {
      const matkul = document.getElementById("matkul").value;
      if (matkul) {
        alert(`Mulai belajar: ${matkul}`);
        // window.location.href = "belajar.html?matkul=" + encodeURIComponent(matkul); // jika ingin redirect
      } else {
        alert("Silakan pilih mata kuliah terlebih dahulu.");
      }
    });
  }

  // Inisialisasi awal
  updateMatkulOptions();
});