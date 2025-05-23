-- UART register accessor by VHDLwhiz
-- Generated with the command:
-- python .\uart_regs-1.0.4\gen_uart_regs.py glitch_delay=32:out:std_logic_vector start_glitch=1:out:std_logic
  
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity uart_regs is
  generic (
    clk_hz : positive;
    baud_rate : positive := 115200
  );
  port (
    clk : in std_logic;
    rst : in std_logic;

    uart_rx : in std_logic;
    uart_tx : out std_logic;

    -- UART accessible registers
    glitch_delay : out std_logic_vector(31 downto 0);
    start_glitch : out std_logic
  );
end uart_regs;

architecture rtl of uart_regs is

  signal out_regs : std_logic_vector(39 downto 0);

begin

  start_glitch <= out_regs(39);
  glitch_delay <= out_regs(38 downto 7);

  BACKEND : entity work.uart_regs_backend(rtl)
    generic map (
      clk_hz => clk_hz,
      baud_rate => baud_rate,
      in_bytes => 0,
      out_bytes => 5
    )
    port map (
      clk => clk,
      rst => rst,
      uart_rx => uart_rx,
      uart_tx => uart_tx,
      in_regs => "",
      out_regs => out_regs
    );

end architecture;