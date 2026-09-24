! Thin batch adapter to the user's separately installed official MCD 6.1.
! Every row is sampled through CALL_MCD; no direct interpretation of EOF files.
program sample_mcd
  use MCD
  implicit none
  character(len=1024) :: dataset, infile, outfile
  integer :: n, i, status, ios, scenario, zkey
  integer :: keys(100)
  real :: z, lon, lat, lt, p, rho, t, u, v, seed
  real :: means(5), extra(100)
  double precision :: ls
  call get_command_argument(1, dataset)
  call get_command_argument(2, infile)
  call get_command_argument(3, outfile)
  open(10,file=trim(infile),status='old',action='read')
  open(11,file=trim(outfile),status='replace',action='write')
  read(10,*) n
  keys=0
  keys(18)=1
  keys(25:28)=1
  keys(59:61)=1
  do i=1,n
    read(10,*,iostat=ios) z,lon,lat,ls,lt,scenario,zkey
    if (ios /= 0) stop 2
    call call_mcd(zkey,z,lon,lat,0,1,ls,lt,trim(dataset),scenario, &
       1,0.0,0.0,keys,p,rho,t,u,v,means,extra,seed,status)
    write(11,'(I4,18(1X,ES18.10E3))') status,p,rho,t,u,v,extra(18), &
       extra(25),extra(26),extra(27),extra(28),extra(59),extra(60),extra(61), &
       extra(1),extra(2),extra(3),extra(4),extra(10)
  end do
  close(10)
  close(11)
end program
