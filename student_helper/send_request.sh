# Simple request
## 
SIZE_OF_INT=4
ORIGINAL_TEXT="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed dapibus velit ac elit bibendum, et mattis dui dictum. Integer tempor lacinia nisl, ultrices convallis ante pellentesque nec. In hac habitasse platea dictumst. Vivamus consectetur ante ut gravida."
PATTERNS="Lorem ipsum dolor sit amet, consectetur adipiscing elit aliquam.Suspendisse euismod consequat risus. Aliquam erat volutpat eget." 
PATTERN_SIZE=16
MAT_SIZE=$(echo "scale=0; sqrt(${#ORIGINAL_TEXT}/${SIZE_OF_INT})" | bc)
NB_PATTERNS=$(echo "${#PATTERNS}/(${PATTERN_SIZE}*4)" | bc)

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
