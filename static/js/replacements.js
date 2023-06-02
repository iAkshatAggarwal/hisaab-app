function editRow(button) {
        // Get the table row element
        let row = button.closest("tr");
        // Hide the "Edit" button and show the "Save" button
        row.querySelector(".btn-outline-primary").classList.add("d-none");
        row.querySelector(".btn-outline-success").classList.remove("d-none");
        // Make all the table cells in the row (except Actions) editable
        row.querySelectorAll("td:not(:last-child)").forEach((cell) => {
          cell.setAttribute("contenteditable", "true");
          cell.setAttribute("data-old-value", cell.textContent);
        });
        event.preventDefault(); // prevent scrolling up
      }

      function saveRow(button) {
          // Get the table row element
          let row = button.closest("tr");
        
          // Get the updated values of each cell
          let rid = row.cells[0].textContent;
          let date = row.cells[2].textContent;
          let pname = row.cells[3].textContent;
          let qty = row.cells[4].textContent;
          let amt = row.cells[5].textContent;
          
          // Send an AJAX request to update the product
          let xhr = new XMLHttpRequest();
          xhr.open("POST", "/replacements/update");
          xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
          xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
              if (xhr.status === 200) {
                // Update successful, hide the "Save" button and show the "Update" button again
                row.querySelector(".btn-outline-success").classList.add("d-none");
                row.querySelector(".btn-outline-primary").classList.remove("d-none");
                // Make all the table cells in the row non-editable
                row.querySelectorAll("td").forEach((cell) => {
                  cell.setAttribute("contenteditable", "false");
                  cell.removeAttribute("data-old-value");
                });
              } else {
                // Error occurred
                console.error(xhr.responseText);
              }
            }
          };
        xhr.send(`rid=${rid}&date=${date}&pname=${pname}&qty=${qty}&amt=${amt}`);
}