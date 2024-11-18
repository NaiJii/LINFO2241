# Simple request
## 
SIZE_OF_INT=4
ORIGINAL_TEXT="AWOOOOOHAWOOOOOH"
PATTERNS="AWAW" 
PATTERN_SIZE=2
MAT_SIZE=2
NB_PATTERNS=2

TRANSFORMATION_MATRIX_FILE="transformation_matrix"

# Constructing the request
## Here we have an identity matrix

echo "MATRIX_SIZE : ${MAT_SIZE}"
echo "NB_PATTERNS : ${NB_PATTERNS}"
echo "PATTERN_SIZE : ${PATTERN_SIZE}"
## Removing prevous file
rm ${TRANSFORMATION_MATRIX_FILE}
for i in $(seq 1 $(( ${MAT_SIZE}-1 ))); do
    echo -n -e \\x01\\x00\\x00\\x00 >> "${TRANSFORMATION_MATRIX_FILE}"
    for j in $(seq 1 ${MAT_SIZE}); do
        echo -n -e \\x00\\x00\\x00\\x00 >> "${TRANSFORMATION_MATRIX_FILE}"
    done
done
echo -n -e \\x01\\x00\\x00\\x00 >> "${TRANSFORMATION_MATRIX_FILE}"

echo "Transformation matrix constructed"

echo -n "${MAT_SIZE}," > request
echo -n "${NB_PATTERNS}," >> request
echo -n "${PATTERN_SIZE}," >> request
echo -n ${ORIGINAL_TEXT} >> request
cat ${TRANSFORMATION_MATRIX_FILE} >> request
echo -n ${PATTERNS} >> request
echo "REQUEST_SIZE : "$(stat --format=%s request)
wget --method=POST --header="Content-Type: application/octet-stream" --body-file=request --output-document=out.bin http://localhost:8888/
# Wait for the server to finish
sleep 2
# Printing the response
printf "\n"
cat out.bin
printf "\n"
