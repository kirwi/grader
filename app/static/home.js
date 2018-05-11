$(document).ready(function() {

  $('#sidebarCollapse').on('click', function() {
    $('#sidebar').toggleClass('active');
  });

  var gradeTable = document.getElementById('grade-table');

  function changeGrade(e){
    var td = e.target;
    var oldGrade = td.innerHTML.trim();
    td.innerHTML = `<input placeholder="${oldGrade}"/>`;
    gradeTable.removeEventListener('click', changeGrade);
    td.addEventListener('keypress', enterGrade);
  }

  function enterGrade(e){
    var key = e.keyCode;
    var input = e.target;
    var td = input.parentElement;
    if (key === 13) {
      var score = input.value.trim();
      var email = td.getAttribute('data-email');
      var title = td.getAttribute('data-title');
      console.log(email, title, score);
      td.innerHTML = score;
      var xhttp = new XMLHttpRequest();
      xhttp.open('GET', `/updateassignment/${title}/${email}/${score}`, true);
      xhttp.send();
      gradeTable.addEventListener('click', changeGrade);
    }
  }

  gradeTable.addEventListener('click', changeGrade);

});
