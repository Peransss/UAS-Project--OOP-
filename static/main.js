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

  // Contoh data, sesuaikan dengan backend
  const matkulBySemester = {
    1: ["Pemrograman Dasar", "Statistik dan Probabilitas", "Matematika Diskrit", "Pengantar Teknologi Informasi"],
    2: ["Struktur Data", "Aljabar Linier", "Pemrograman Berorientasi Objek", "Logika Matematika"]
  };

  // Fungsi untuk mengisi pilihan mata kuliah sesuai semester
  function updateMatkulOptions() {
    const semester = document.getElementById("semester").value;
    const matkulSelect = document.getElementById("matkul");
    matkulSelect.innerHTML = "";
    matkulBySemester[semester].forEach(function(matkul) {
      const opt = document.createElement("option");
      opt.value = matkul;
      opt.textContent = matkul;
      matkulSelect.appendChild(opt);
    });
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
      const matkul = document.getElementById("matkul").value;
      if (!matkul) {
        e.preventDefault();
        alert("Silakan pilih mata kuliah terlebih dahulu!");
      }
    });
  }

  // Inisialisasi awal
  updateMatkulOptions();

  // Agar radio button "role" bisa di-uncheck jika diklik dua kali (khusus halaman login)
  document.querySelectorAll('input[type=radio][name=role]').forEach(function(radio) {
    radio.addEventListener('mousedown', function(e) {
      if (this.checked) {
        this.wasChecked = true;
      } else {
        this.wasChecked = false;
      }
    });
    radio.addEventListener('click', function(e) {
      if (this.wasChecked) {
        this.checked = false;
        this.wasChecked = false;
        e.preventDefault();
      }
    });
  });
});