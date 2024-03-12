const overlay = document.getElementById("overlay");
const form = document.getElementById("upload-file-form");
const scoreBtn = document.getElementById("score-btn");
const round2Wrapper = document.getElementById("round2-wrapper");
const round2ScoreBtn = document.getElementById("check-round2-btn");
const extractedTextContainer = document.querySelector(
    ".extracted-text-container"
);
var fileInput  = document.querySelector( ".input-file" ),
button     = document.querySelector( ".input-file-trigger" ),
the_return = document.querySelector(".file-return");
const round1TableContainer = document.getElementById(
    "round1-table-container"
);
const round1tbody = document.getElementById("round1-tbody");
const round1Score = document.getElementById("round1-score");
const round1ScoreStatus = document.getElementById(
    "round1-score-status"
);
const round1FailReason = document.getElementById("round1-fail-reason");
const round1FailReasonContent =
document.getElementById("round1-reason-content");
const round2TableContainer = document.getElementById(
    "round2-table-container"
);
const round2tbody = document.getElementById("round2-tbody");
const round2Score = document.getElementById("round2-score");
const round2ScoreStatus = document.getElementById(
    "round2-score-status"
);
const round2FailReason = document.getElementById("round2-fail-reason");
const round2FailReasonContent =
document.getElementById("round2-reason-content");
const setLoading = (loadingState) => {
    if (loadingState) {
        overlay.style.display = "flex";
    } else {
        overlay.style.display = "none";
    }
};
button.addEventListener( "keydown", function( event ) {
    if ( event.keyCode == 13 || event.keyCode == 32 ) {
        fileInput.focus();
    }
});
button.addEventListener( "click", function( event ) {
    fileInput.focus();
    return false;
});
fileInput.addEventListener( "change", function( event ) {
    const fileName = this.value.split("\\").pop();
    the_return.innerHTML = fileName;
});
form.addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission

    setLoading(true);
    extractedTextContainer.style.display = "none";
    scoreBtn.style.display = "none";
    round1TableContainer.style.display = "none";
    round2TableContainer.style.display = "none";
    const formData = new FormData();
    var the_return = document.querySelector(".file-return");
    const file = document.getElementById("file").files[0];
    formData.append("file", file);

    try {
        const res = await fetch("/extract-text", {
            method: "POST",
            body: formData,
        });
        round1TableContainer.style.display = "block";
        const data = await res.json();

        if (res.ok) {
            extractedTextContainer.style.display = "flex";
            const fileContent = document.getElementById("file-content");
            fileContent.innerHTML = data.extracted_text;
            scoreBtn.style.display = "block";
        } else {
            console.log(data);
        }
    } catch (error) {
        console.log(error);
    } finally {
        setLoading(false);
    }
});

scoreBtn.addEventListener("click", async (event) => {
    event.preventDefault();

    setLoading(true);

    try {
        const res = await fetch("/analyze-pdf", {
            method: "GET",
        });
        const data = await res.json();
        console.log(data)
        const parsedData = JSON.parse(data.data);
        let totalScore = data.score;

        parsedData.forEach(function (rowData, index) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.textContent = index + 1;
            row.appendChild(cell);
            for (const key in rowData) {
                const cell = document.createElement("td");
                cell.textContent = rowData[key];
                row.appendChild(cell);
            }
            round1tbody.appendChild(row);
        });

        round1Score.textContent = `Round 1 Score: ${totalScore}`;
        round1TableContainer.style.display = "block";
        if (totalScore >= 40) {
            round1ScoreStatus.textContent = "Round 1 Cleared";
            round1ScoreStatus.style.color = "green";
            round2Wrapper.style.display = "block";
        } else {
            round1ScoreStatus.textContent = "Round 1 Failed";
            round1ScoreStatus.style.color = "red";
            round1FailReason.style.display = "block";
            round1FailReasonContent.textContent = data.reason;
        }
    } catch (error) {
        console.log(error);
    } finally {
        setLoading(false);
    }
});

round2ScoreBtn.addEventListener("click", async (event) => {
    event.preventDefault();

    setLoading(true);

    try {
        const res = await fetch("/check-round-two", {
            method: "GET",
        });
        const data = await res.json();
        const totalScore = data.total_score;
        const parsedData = JSON.parse(data.data);

        parsedData.forEach(function (rowData, index) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.textContent = index + 1;
            row.appendChild(cell);
            for (const key in rowData) {
                const cell = document.createElement("td");
                cell.textContent = rowData[key];
                row.appendChild(cell);
            }
            round2tbody.appendChild(row);
        });

        round2Score.textContent = `Total Score: ${totalScore || 0}`;
        if (totalScore >= 60) {
            round2ScoreStatus.textContent = "Round 2 Cleared";
            round2ScoreStatus.style.color = "green";
        } else {
            round2ScoreStatus.textContent = "Round 2 Failed";
            round2ScoreStatus.style.color = "red";
            round2FailReason.style.display = "block";
            round2FailReasonContent.textContent = data.reason;
        }
        round2TableContainer.style.display = "block";
    } catch (error) {
        console.log(error);
    } finally {
        setLoading(false);
    }

});
//function resetZoom() {
//  alert('You can reset the zoom level to 100% using your browser settings or keyboard shortcuts:\n- Ctrl + 0 (on Windows/Linux)\n- Cmd + 0 (on macOS)');
//}
//resetZoom();
//var scale = 'scale(1)';document.body.style.webkitTransform =  scale;    // Chrome, Opera, Safaridocument.body.style.msTransform =   scale;       // IE 9document.body.style.transform = scale;

//var scale = 'scale(1)';
//document.body.style.webkitTransform =  scale;    // Chrome, Opera, Safaridocument.body.style.msTransform =   scale;       // IE 9document.body.style.transform = scale;