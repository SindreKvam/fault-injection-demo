-- UART register accessor by VHDLwhiz

  constant clk_hz : integer := 100e6;

  signal clk : std_logic;
  signal rst : std_logic;
  signal uart_to_dut : std_logic;
  signal uart_from_dut : std_logic;

  -- UART accessible registers
  signal glitch_delay : std_logic_vector(31 downto 0);
  signal start_glitch : std_logic;

begin

  -- Generated with the command:
  -- python .\uart_regs-1.0.4\gen_uart_regs.py glitch_delay=32:out:std_logic_vector start_glitch=1:out:std_logic
  UART_REGS_INST : entity work.uart_regs(rtl)
  generic map (
    clk_hz => clk_hz
  )
  port map (
    clk => clk,
    rst => rst,
    uart_rx => uart_rx,
    uart_tx => uart_tx,
    glitch_delay => glitch_delay,
    start_glitch => start_glitch
  );
  