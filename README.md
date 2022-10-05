# Moving-Balls
The algorithm aims to find the arrangement where no active particles overlap in the cathode. The particles are allocated 
inside the cathode randomly at the start, which means some particles might overlap, and some might not. 
The overlap function is calculated, which is the sum of the overlapping distance of each ball pair, 
and it is zero when the final arrangement has been reached. To reduce the function to zero, the particles are randomly selected to perform a move. 
The move is rejected if it increases the overlap function; otherwise, it is accepted.




