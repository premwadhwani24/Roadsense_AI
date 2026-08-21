package com.ai.smart.road.monitoring.system.application.gui.components;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.util.List;

import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;

import com.ai.smart.road.monitoring.system.application.dto.RepairActivityDTO;

public class RepairStatusPanel extends JPanel {
	
	private static final long serialVersionUID = 1L;

	private JTable repairTable;
	private DefaultTableModel tableModel;

	public RepairStatusPanel(List<RepairActivityDTO> repairs) {
		setLayout(new BorderLayout());
		setPreferredSize(new Dimension(600, 300));

		String[] columns = { "Pothole ID", "Status", "Repair Date", "Technician" };
		tableModel = new DefaultTableModel(columns, 0);
		repairTable = new JTable(tableModel);
		populateTable(repairs);

		add(new JScrollPane(repairTable), BorderLayout.CENTER);
	}

	public void populateTable(List<RepairActivityDTO> repairs) {
		tableModel.setRowCount(0); // clear previous rows
		if (repairs != null) {
			for (RepairActivityDTO r : repairs) {
				tableModel
						.addRow(new Object[] { r.getPotholeId(), r.getStatus(), r.getRepairDate(), r.getTechnician() });
			}
		}
	}
}
